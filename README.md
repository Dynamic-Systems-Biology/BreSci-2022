# Integrated Database
This software aggregates Sabio-RK information to a pre-existent Neo4J Reactome Graph Database.

# Before you Start!

- Before use this software, please install **Neo4J Desktop** version and add the latest version of **Reactome Graph Database**, according their instructions.
- Once downloaded, create a folder called "**.env**" in the project main folder. This will contain your local information to be able to add the new nodes.
- Before using the software, open Neo4J Desktop and run the **Reactome Graph Database**, after this, you're ready to use the program.

# .env File Model

scheme = "neo4j" <br>
host_name = "localhost" <br>
database = graph.db <br>
port = **Your Port** <br>
user = **Your Username** <br>
password = **Your Password** <br>
<br>

# tmp Folder

In order to be able to get all statistics, please consider creating a directory called "tmp". All the information obtained by Anguix will be displayed in a .csv file inside this folder.

# Running the Software:

- Once started, the software will check for dependencies and display basic information about both Sabio-RK and Reactome.
- The software will ask if you want to operate in **Auto** or **Manual** mode:

# Auto Mode:

The auto mode will seek for all organisms in common for both Sabio-RK and Reactome, and will add them to the graph. Due to Sabio-RK server timeout, this mode tends to be very time consuming.

# Manual Mode:

Adds only available reactions from a single desired organism. The list will be displayed to the user.

# The Outcome

If everything works fine, the reactions will be displayed on the Reactome Graph Database, and you will be able to use it as you wish.

# How to Check if the Reactions Were Added:

When accessing your graph, you can reach for Sabio-RK reactions with the following cypher query: <br><br>

**// SELECT ALL REACTIONS** <br>
**MATCH** (n:SabioRkReaction)-[:KinecticDatafor]-(k), (n)-[:GeneralReactionFor]-(r), (k)-[:ParameterInfo]->(p) <br>
**RETURN** n, k, r, p <br>

# If you Regreted Using Anguix and Desire to Remove All Added Information:

**// ERASE ALL REACTIONS** <br>
**MATCH** (n:SabioRkReaction)-[:KinecticDatafor]-(k), (n)-[:GeneralReactionFor]-(r), (k)-[:ParameterInfo]->(p) <br>
**DETACH DELETE** n, k, p <br>
