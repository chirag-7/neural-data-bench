# N05 repair revision2

Original object traversal deduplicates aliases. Round1 link traversal ignored internal SoftLinks and did not recursively follow alias groups. Revision2 walks metadata paths, follows internal hard/soft links, refuses external-file links and uses ancestor object addresses to prevent cycles. Existing role/unit/sweep selection and numerical calculations remain unchanged. No expected answers or measured numerical constants added. Original249line noncompliance remains visible; no cosmetic trimming.
