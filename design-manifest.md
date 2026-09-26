# Design Manifest

### 🎥 Presentation: **[youtu.be/sqv3Oi22v5w](https://youtu.be/sqv3Oi22v5w?si=4DbluZcx6Qlugwai)**

This manifest documents the AI tooling used to produce the project and the role each tool served across the development process. It is limited to tooling; the analytical methodology and findings are documented on the [project site](https://jconnors23.github.io/510-m1-nfl-data-storytelling/).

## Tooling Summary

| Stage | Tool | Function |
| :--- | :--- | :--- |
| Ideation | Gemini | Problem framing, scope definition, and dataset identification |
| Implementation | Cursor | Feature-engineering code, data transformation, and figure generation |
| Documentation | Kiro | Documentation site, README, code comments, and project formalization |
| Presentation visuals | Gemini, ChatGPT | Image assets for the presentation slides |

## Ideation — Gemini

Gemini was used for problem framing and dataset identification. It supported the reduction of a broad subject area (NFL performance data) to a single, testable question: whether a team's win–loss record and its point differential rank the same team differently. Gemini was used to define the scope that constrains the rest of the project — the 2024 regular season, all 32 teams, two independent rankings, and the gap between them. It was also used to identify publicly available datasets suitable for answering that question, which led to the selection of the nflverse schedules release as the data source.

## Implementation — Cursor

Cursor was used to author the analysis code. Its outputs include the data-acquisition script that retrieves the nflverse schedules, the transformation logic that reshapes 272 game records into a 32-team table, and the derived columns on which the analysis depends: the two rankings, the ranking gap, and the mismatch flag. Cursor also authored the plotting code that generates every figure — the record-versus-point-differential scatter, the mismatch dumbbell, the ranking-gap distribution, and the feature-map chart. All executable code and data transformations originate from Cursor.

## Documentation — Kiro

Kiro was used to produce the documentation from the completed code and data. Its work covers the [MkDocs documentation site](https://jconnors23.github.io/510-m1-nfl-data-storytelling/) (project overview, feature engineering, reproduction pipeline, exploratory data analysis, and conclusions), the repository README, and the code comments. In addition to authoring prose, Kiro was used to formalize the project's structure and enforce consistency: establishing a single reading order, consolidating duplicated logic and figures, verifying quoted statistics against the source table, correcting figure captions and chart labels, and validating the site with a strict MkDocs build. All version-control operations were reserved to the author; Kiro modified working files only.

## Presentation Visuals — Gemini and ChatGPT

Gemini and ChatGPT were used to generate the image assets that support the presentation slides. The analytical charts on the slides are the figures produced by Cursor; the tool-generated images provide the surrounding visual design only.
