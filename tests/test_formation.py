"""Tests de non-régression de la formation Beobank.

Lancer depuis la racine du dépôt :
    python -m pytest tests -v

Vérifie :
  1. que les 5 CSV de data/ se chargent (séparateur ";", colonnes attendues) ;
  2. que chaque chemin relatif cité dans un notebook (../../data/..., liens .ipynb) existe ;
  3. que chaque notebook s'exécute de bout en bout sans erreur inattendue.

Les notebooks sont exécutés dans une copie temporaire du dépôt : les fichiers
d'origine et le dossier output/ ne sont jamais modifiés.
"""
import re
import shutil
from pathlib import Path

import nbformat
import pandas as pd
import pytest
from nbclient import NotebookClient

RACINE = Path(__file__).resolve().parent.parent
DATA = RACINE / "data"
NOTEBOOKS = sorted(p for p in RACINE.glob("Jour_*/*/*.ipynb"))
BLANC = "______"  # trou à compléter dans les cahiers participants

COLONNES_ATTENDUES = {
    "CTR.csv": {"IDT_AC", "DAT_OUV_CTR", "COD_ECV_CTR", "COD_DEV", "SLD_CTR"},
    "TIE.csv": {"NUM_TIE", "DAT_NAI"},
    "TIE_ADR.csv": {"NUM_TIE", "DAT_MAJ_ADR"},
    "TIE_X_CTR.csv": {"NUM_TIE", "IDT_AC"},
    "TXN_X_CTR.csv": {"IDT_AC", "DAT_CRE_MVT_CPB"},
}


def nom(p):
    return str(p.relative_to(RACINE)).replace("\\", "/")


# ---------------------------------------------------------------- 1. données
@pytest.mark.parametrize("fichier", sorted(COLONNES_ATTENDUES))
def test_dataset_se_charge(fichier):
    df = pd.read_csv(DATA / fichier, sep=";")
    assert len(df) > 0, f"{fichier} est vide"
    manquantes = COLONNES_ATTENDUES[fichier] - set(df.columns)
    assert not manquantes, f"{fichier} : colonnes manquantes {manquantes}"


def test_structure_des_jours():
    jours = sorted(p.name for p in RACINE.glob("Jour_*") if p.is_dir())
    assert len(jours) == 3, jours
    assert NOTEBOOKS, "aucun notebook trouvé"
    for nb in NOTEBOOKS:
        assert len(str(nb)) < 240, f"chemin trop long pour Windows : {nb}"


CHAPITRES = sorted(p for p in RACINE.glob("Jour_*/*") if p.is_dir())


def nb_trous(nb_path):
    nb = nbformat.read(nb_path, as_version=4)
    return sum(c.source.count(BLANC) for c in nb.cells if c.cell_type == "code")


@pytest.mark.parametrize("chapitre", CHAPITRES, ids=nom)
def test_chaque_chapitre_a_un_cahier_a_trous(chapitre):
    trous = {p.name: nb_trous(p) for p in chapitre.glob("*Participants*.ipynb")}
    assert trous and max(trous.values()) >= 20, f"aucun cahier participant à 20 trous minimum : {trous}"


@pytest.mark.parametrize("chapitre", [c for c in CHAPITRES if (c / "Scenario_Exercices_Participants.ipynb").exists()], ids=nom)
def test_scenario_et_corrige_alignes(chapitre):
    if not (chapitre / "Scenario_Corrige_Formateur.ipynb").exists():
        pytest.skip("corrigé absent (version participants, exclue par .gitignore)")
    participant = nbformat.read(chapitre / "Scenario_Exercices_Participants.ipynb", as_version=4)
    corrige = nbformat.read(chapitre / "Scenario_Corrige_Formateur.ipynb", as_version=4)
    assert [c.cell_type for c in participant.cells] == [c.cell_type for c in corrige.cells]
    assert nb_trous(chapitre / "Scenario_Corrige_Formateur.ipynb") == 0, "trou oublié dans le corrigé"


# ---------------------------------------------------------------- 2. chemins
CHEMIN_RELATIF = re.compile(r"((?:\.\./)+[\w./-]+\.(?:csv|ipynb|png))")


@pytest.mark.parametrize("nb_path", NOTEBOOKS, ids=nom)
def test_chemins_relatifs_existent(nb_path):
    nb = nbformat.read(nb_path, as_version=4)
    casses = set()
    for cell in nb.cells:
        for chemin in CHEMIN_RELATIF.findall(cell.source):
            if "output/" in chemin or BLANC in chemin:  # fichier produit par le notebook / trou d'exercice
                continue
            if cell.cell_type == "markdown" and chemin.endswith(".csv"):  # exemple générique (NOM.csv)
                continue
            if not (nb_path.parent / chemin).resolve().exists():
                casses.add(chemin)
    assert not casses, f"chemins introuvables : {sorted(casses)}"


# ---------------------------------------------------------------- 3. exécution
@pytest.fixture(scope="session")
def copie_depot(tmp_path_factory):
    dst = tmp_path_factory.mktemp("r")
    for p in [DATA, *RACINE.glob("Jour_*")]:
        shutil.copytree(p, dst / p.name)
    return dst


def executer(nb_path):
    nb = nbformat.read(nb_path, as_version=4)
    client = NotebookClient(nb, timeout=180, kernel_name="python3", allow_errors=True,
                            resources={"metadata": {"path": str(nb_path.parent)}})
    client.execute()
    erreurs = []
    for i, cell in enumerate(nb.cells):
        for out in cell.get("outputs", []) if cell.cell_type == "code" else []:
            if out.output_type == "error":
                erreurs.append((i, out.ename, out.evalue[:200], cell.source))
    return nb, erreurs


def sortie_texte(nb):
    return "".join(o.get("text", "") for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", []))


@pytest.mark.parametrize("nb_path", NOTEBOOKS, ids=nom)
def test_notebook_s_execute(nb_path, copie_depot):
    copie = copie_depot / nb_path.relative_to(RACINE)
    nb, erreurs = executer(copie)

    # Aucune erreur de fichier ou de module, quel que soit le notebook
    bloquantes = [e for e in erreurs if e[1] in ("FileNotFoundError", "ModuleNotFoundError", "ImportError")]
    assert not bloquantes, "\n".join(f"cellule {i} {n}: {v}" for i, n, v, _ in bloquantes)

    # input() ne peut pas être exécuté en mode automatique : attendu en salle, pas une erreur
    erreurs = [e for e in erreurs if e[1] != "StdinNotImplementedError"]

    if "Vertica" in nb_path.name and "Connexion Vertica impossible" in sortie_texte(nb):
        pytest.skip("pas de serveur Vertica accessible : seules les erreurs de fichier/module sont vérifiées")

    if any(BLANC in c.source for c in nb.cells if c.cell_type == "code"):
        # Cahier à trous : tout ce qui précède le premier trou (chargement, setup) doit passer
        premier_trou = next(i for i, c in enumerate(nb.cells) if c.cell_type == "code" and BLANC in c.source)
        erreurs = [e for e in erreurs if e[0] < premier_trou]

    assert not erreurs, "\n".join(f"cellule {i} {n}: {v}\n    {s[:150]!r}" for i, n, v, s in erreurs)
