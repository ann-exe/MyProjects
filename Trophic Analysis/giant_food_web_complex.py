from pyvis.network import Network
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set()

columns = ["source_taxon_name", "source_taxon_path", "interaction_type", "target_taxon_name", "target_taxon_path"]
df = pd.read_csv("interaction.csv")[columns]
df.rename(columns={"source_taxon_name": "Species_1", "source_taxon_path": "Kingdom_1",
                   "interaction_type": "Interaction_type", "target_taxon_name": "Species_2",
                   "target_taxon_path": "Kingdom_2"}, inplace=True)

print(df.head())

text_plant = "Plantae"
text_fungus = "Fungi"
text_animal = "Animalia"
text_root = "root"


df.loc[df["Kingdom_1"].str.contains(text_plant, case=False, na=False), "Kingdom_1"] = "Plant"
df.loc[df["Kingdom_1"].str.contains(text_fungus, case=False, na=False), "Kingdom_1"] = "Fungi"
df.loc[df["Kingdom_1"].str.contains(text_animal, case=False, na=False), "Kingdom_1"] = "Animal"
df.loc[df["Kingdom_1"].str.contains(text_root, case=False, na=False), "Kingdom_1"] = "Animal"

df.loc[df["Kingdom_2"].str.contains(text_plant, case=False, na=False), "Kingdom_2"] = "Plant"
df.loc[df["Kingdom_2"].str.contains(text_fungus, case=False, na=False), "Kingdom_2"] = "Fungi"
df.loc[df["Kingdom_2"].str.contains(text_animal, case=False, na=False), "Kingdom_2"] = "Animal"
df.loc[df["Kingdom_2"].str.contains(text_root, case=False, na=False), "Kingdom_2"] = "Animal"

df.to_csv(path_or_buf="Giant_web.csv", index=False)

condition = df["Interaction_type"].str.contains("eats|eatenBy", case=False, na=False)

df = df.loc[condition]

df.to_csv(path_or_buf="Giant_web_eating.csv", index=False)

condition = df["Interaction_type"] == "eatenBy"
df.loc[condition, ["Species_1", "Kingdom_1", "Species_2", "Kingdom_2"]] = \
    df.loc[condition, ["Species_2", "Kingdom_2", "Species_1", "Kingdom_1"]].values

df = df.drop(columns=["Interaction_type"])
df = df.drop_duplicates()

df.to_csv(path_or_buf="Giant_web_eating_by.csv", index=False)

network = Network(notebook=True, directed=True, cdn_resources="remote")
network.force_atlas_2based()

unique_nodes = set()

for _, row in df.iterrows():
    if row["Species_1"] not in unique_nodes:
        network.add_node(row["Species_1"], label=row["Species_1"], title=row["Kingdom_1"],
                         color="#F3911C" if row["Kingdom_2"] == "Plant" else "#F31C26")
        unique_nodes.add(row["Species_1"])

    if row["Species_2"] not in unique_nodes:
        network.add_node(row["Species_2"], label=row["Species_2"], title=row["Kingdom_2"],
                         color="#A5EE34" if row["Kingdom_2"] == "Plant" else "#F3911C")
        unique_nodes.add(row["Species_2"])

    network.add_edge(row["Species_1"], row["Species_2"], title="consumes")

network.show("giant_food_web_complex.html", notebook=True)

n_network = nx.DiGraph()

unique_nodes = set()

for _, row in df.iterrows():
    if row["Species_1"] not in unique_nodes:
        n_network.add_node(row["Species_1"], label=row["Species_1"], title=row["Kingdom_1"],
                           color="#F3911C" if row["Kingdom_2"] == "Plant" else "#F31C26")
        unique_nodes.add(row["Species_1"])

    if row["Species_2"] not in unique_nodes:
        n_network.add_node(row["Species_2"], label=row["Species_2"], title=row["Kingdom_2"],
                           color="#A5EE34" if row["Kingdom_2"] == "Plant" else "#F3911C")
        unique_nodes.add(row["Species_2"])

    n_network.add_edge(row["Species_1"], row["Species_2"], title="consumes")

# Stopnie wierzcholkow z wyroznieniem krolestwa

degrees = [(node, n_network.degree(node), n_network.nodes[node]["title"]) for node in n_network.nodes]
sorted_degrees = sorted(degrees, key=lambda x: x[1], reverse=True)

top_nodes = sorted_degrees[:10]
for node, degree, kingdom in top_nodes:
    print(f"Wierzcholek: {node}, Stopien: {degree}, Krolestwo: {kingdom}")

node_names = [node[0] for node in top_nodes]
node_degrees = [node[1] for node in top_nodes]

kingdom_colors = {"Plant": "#A5EE34", "Animal": "#FC3058"}
node_colors = [kingdom_colors[kingdom] for _, _, kingdom in top_nodes]

plt.figure(figsize=(10, 6))
ax = sns.barplot(x=node_names, y=node_degrees, palette=node_colors, hue=node_names)
ax.set_ylabel("Stopień wierzchołka", labelpad=20)
ax.set_title("Największe stopnie wierzchołków w sieci z zaznaczeniem królestwa", pad=20)
plt.xticks(rotation=90)
plt.tight_layout()

plt.show()

# Stopnie wierzcholkow bez wyroznienia krolestwa

degrees = dict(n_network.degree())
sorted_degrees = sorted(degrees.items(), key=lambda x: x[1], reverse=True)

top_nodes = sorted_degrees[:10]
for node, degree in top_nodes:
    print(f"Wierzcholek: {node}, Stopien: {degree}")

node_names = [node[0] for node in top_nodes]
node_degrees = [node[1] for node in top_nodes]

plt.figure(figsize=(10, 6))
ax = sns.barplot(x=node_names, y=node_degrees, palette="rocket_r", hue=node_names)
ax.set_ylabel("Stopień wierzchołka", labelpad=20)
ax.set_title("Największe stopnie wierzchołków w sieci", pad=20)
plt.xticks(rotation=90)
plt.tight_layout()

plt.show()

# Centralnosc wchodzaca wierzcholkow z wyroznieniem krolestwa

in_centralities = nx.in_degree_centrality(n_network)
degrees = [(node, in_centralities[node], n_network.nodes[node]["title"]) for node in n_network.nodes]
sorted_degrees = sorted(degrees, key=lambda x: x[1], reverse=True)

top_nodes = sorted_degrees[:10]
for node, degree, kingdom in top_nodes:
    print(f"Wierzcholek: {node}, Centralnosc wchodzaca: {degree}, Krolestwo: {kingdom}")

node_names = [node[0] for node in top_nodes]
node_degrees = [node[1] for node in top_nodes]

kingdom_colors = {"Plant": "#A5EE34", "Animal": "#FC3058"}
node_colors = [kingdom_colors[kingdom] for _, _, kingdom in top_nodes]

plt.figure(figsize=(10, 6))
ax = sns.barplot(x=node_names, y=node_degrees, palette=node_colors, hue=node_names)
ax.set_ylabel("Centralność wchodząca wierzchołka", labelpad=20)
ax.set_title("Największe wartości centralności wchodzącej wierzchołków w sieci z zaznaczeniem królestwa", pad=20)
plt.xticks(rotation=90)
plt.tight_layout()

plt.show()

# Centralnosc wchodzaca wierzcholkow bez wyroznienia krolestwa

in_centralities = nx.in_degree_centrality(n_network)
sorted_degrees = sorted(in_centralities.items(), key=lambda x: x[1], reverse=True)

top_nodes = sorted_degrees[:10]
for node, in_centrality in top_nodes:
    print(f"Wierzcholek: {node}, Centralnosc wchodzaca: {in_centrality}")

node_names = [node[0] for node in top_nodes]
node_degrees = [node[1] for node in top_nodes]

plt.figure(figsize=(10, 6))
ax = sns.barplot(x=node_names, y=node_degrees, palette="rocket_r", hue=node_names)
ax.set_ylabel("Centralność wchodząca wierzchołka", labelpad=20)
ax.set_title("Największe wartości centralności wchodzącej wierzchołków w sieci", pad=20)
plt.xticks(rotation=90)
plt.tight_layout()

plt.show()

# Centralnosc wychodzaca wierzcholkow z wyroznieniem krolestwa

out_centralities = nx.out_degree_centrality(n_network)
degrees = [(node, out_centralities[node], n_network.nodes[node]["title"]) for node in n_network.nodes]
sorted_degrees = sorted(degrees, key=lambda x: x[1], reverse=True)

top_nodes = sorted_degrees[:10]
for node, degree, kingdom in top_nodes:
    print(f"Wierzcholek: {node}, Centralnosc wychodzaca: {degree}, Krolestwo: {kingdom}")

node_names = [node[0] for node in top_nodes]
node_degrees = [node[1] for node in top_nodes]

kingdom_colors = {"Plant": "#A5EE34", "Animal": "#FC3058"}
node_colors = [kingdom_colors[kingdom] for _, _, kingdom in top_nodes]

plt.figure(figsize=(10, 6))
ax = sns.barplot(x=node_names, y=node_degrees, palette=node_colors, hue=node_names)
ax.set_ylabel("Centralność wychodząca wierzchołka", labelpad=20)
ax.set_title("Największe wartości centralności wychodzącej wierzchołków w sieci z zaznaczeniem królestwa", pad=20)
plt.xticks(rotation=90)
plt.tight_layout()

plt.show()

# Centralnosc wychodzaca wierzcholkow bez wyroznienia krolestwa

out_centralities = nx.out_degree_centrality(n_network)
sorted_degrees = sorted(out_centralities.items(), key=lambda x: x[1], reverse=True)

top_nodes = sorted_degrees[:10]
for node, out_centrality in top_nodes:
    print(f"Wierzcholek: {node}, Centralnosc wychodzaca: {out_centrality}")

node_names = [node[0] for node in top_nodes]
node_degrees = [node[1] for node in top_nodes]

plt.figure(figsize=(10, 6))
ax = sns.barplot(x=node_names, y=node_degrees, palette="rocket_r", hue=node_names)
ax.set_ylabel("Centralność wychodząca wierzchołka", labelpad=20)
ax.set_title("Największe wartości centralności wychodzącej wierzchołków w sieci", pad=20)
plt.xticks(rotation=90)
plt.tight_layout()

plt.show()

# Stopnie wychodzace wierzcholkow bez wyroznienia krolestwa (rosliny nikogo nie jedza)

degrees = [(node, n_network.out_degree(node)) for node in n_network.nodes]
sorted_degrees = sorted(degrees, key=lambda x: x[1], reverse=True)

nodes_all = sorted_degrees[:10]
top_nodes = []
for node, degree in nodes_all:
    if degree != 0:
        top_nodes.append((node, degree))

for node, degree in top_nodes:
    print(f"Wierzcholek: {node}, Stopien wychodacy: {degree}")

generalistic = 0
specialistic = 0
for node, degree in top_nodes:
    if degree == 1:
        specialistic += 1
    else:
        generalistic += 1

print(f"Ilosc gatunkow generalistycznych: {generalistic}")
print(f"Ilosc gatunkow specjalistycznych: {specialistic}")

node_names = [node[0] for node in top_nodes]
node_degrees = [node[1] for node in top_nodes]

plt.figure(figsize=(10, 6))
ax = sns.barplot(x=node_names, y=node_degrees, palette="rocket_r")
ax.set_ylabel("Stopień wychodzący wierzchołka", labelpad=20)
ax.set_title("Najwieksze stopnie wychodzące wierzchołków w sieci", pad=20)
plt.xticks(rotation=90)
plt.tight_layout()

plt.show()
