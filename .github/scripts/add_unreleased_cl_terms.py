"""Add CL terms used in annotation.tsv but missing from the SemSQL cl.db.

cas2rdf checks every cell_ontology_term_id against CL's descendants of
CL:0000000, which it reads from the SemSQL cl.db. That file is built from the
latest CL release, so terms minted on CL master since then are rejected. This
adds each missing term as a subclass of CL:0000000, labelled as in the
annotation table, so the export can run before the next CL release reaches
SemSQL. Once it does, the script finds nothing to add.

Usage: add_unreleased_cl_terms.py <annotation.tsv> <cl.db>
"""
import csv
import sqlite3
import sys


def main(annotation_tsv, cl_db):
    with open(annotation_tsv, newline="") as f:
        terms = {
            row["cell_ontology_term_id"]: row["cell_ontology_term"]
            for row in csv.DictReader(f, delimiter="\t")
            if row.get("cell_ontology_term_id", "").startswith("CL:")
        }

    con = sqlite3.connect(cl_db)
    known = {
        s
        for (s,) in con.execute(
            "SELECT DISTINCT subject FROM entailed_edge "
            "WHERE predicate = 'rdfs:subClassOf' AND object = 'CL:0000000'"
        )
    }
    missing = sorted(set(terms) - known)
    for curie in missing:
        print(f"WARNING: {curie} ({terms[curie]}) is not in cl.db; adding it as a cell type.")
        con.execute(
            "INSERT INTO statements (stanza, subject, predicate, object) VALUES (?, ?, 'rdf:type', 'owl:Class')",
            (curie, curie),
        )
        con.execute(
            "INSERT INTO statements (stanza, subject, predicate, value, datatype) VALUES (?, ?, 'rdfs:label', ?, 'xsd:string')",
            (curie, curie, terms[curie]),
        )
        con.executemany(
            "INSERT INTO entailed_edge (subject, predicate, object) VALUES (?, 'rdfs:subClassOf', ?)",
            [(curie, curie), (curie, "CL:0000000")],
        )
    con.commit()
    con.close()
    print(f"{len(missing)} CL term(s) added to {cl_db}.")


if __name__ == "__main__":
    main(*sys.argv[1:])
