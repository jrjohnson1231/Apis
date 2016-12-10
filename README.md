DS Final Project - Apis
=======================

Apis:
-----

Apis is a system that anaylzes a network of specific links in order to provide the user with suggestions of links that they may be interested in visiting, based off of the provided link(s).

Project Dependencies:
---------------------

Set-up & Installation:
----------------------

Code Execution:
---------------
- **To make honeybee**:

> make

- **To test honeybee**:

> make test

- **To run scout.py and create nectar.txt (default output is output.txt, use -h tag for more usage information)**:

> ./scout.py -o nectar.txt

- **To run honeybee's usage (and learn how to run BFS and random step versions)**:

> ./honeybee -h

- **To run the server, hive.py**:

> # Set FLASK_APP environment variable to hive.py 
> export FLASK_APP=hive.py # bash syntax
> flask run

- **To benchmark everything, do**:

> chmod 775 benchmark.sh

> ./benchmark.sh

Other Relevant Information:
---------------------------

- For member contributions, please see `CONTRIBUTORS.md`.

- No bees were harmed in the making of this project

Members:
--------
- Kylie Hausch (khausch)

- Shelby Lem (slem)

- John Johnson (jjohns48)

- Nikolas Dean Brooks (nbrooks3)