# The corpus

Two curriculum documents, used as the knowledge base in block 4.

| File | Document | Pages |
|---|---|---|
| `mtech-data-science-2024.txt` | M. Tech. in Data Science — Curriculum & Syllabus 2024 | 74 |
| `mtech-artificial-intelligence-2024.txt` | M. Tech. in Artificial Intelligence — Curriculum & Syllabus 2024 | 86 |

## Where these came from

Both are published by Amrita Vishwa Vidyapeetham on its own public web host, and
were downloaded from these addresses:

- https://webfiles.amrita.edu/2024/08/mtech-data-sciences-curriculum-syllabus-2024.pdf
- https://webfiles.amrita.edu/2024/09/m-tech-artificial-intelligence-curriculum-syllabus-2024.pdf

Only the text layer is stored here, to keep the repository small. To regenerate
it from the originals:

```bash
curl -LO https://webfiles.amrita.edu/2024/08/mtech-data-sciences-curriculum-syllabus-2024.pdf
pdftotext -layout mtech-data-sciences-curriculum-syllabus-2024.pdf mtech-data-science-2024.txt
```

Nothing internal to the University is included. Documents that live only on the
campus intranet were deliberately left out, because this repository is public.

## Why two documents and not one

Because retrieval only becomes interesting when the wrong answer is available.
The two programmes share a great deal of vocabulary — both teach machine
learning, both have a project semester, both list electives with similar names.
A retriever that simply matches on the word "elective" will pull from whichever
document happens to sit first in the index.

Block 4 asks questions that are answerable from exactly one of them. Getting the
right passage back therefore means something. With a single document it would
not.
