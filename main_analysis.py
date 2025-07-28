# main_analysis.py
import os
import numpy as np
from ete3 import Tree
import itertools

def add_internal_node_names(t):
    """Asigna nombres a los nodos internos de un árbol (ej. N1, N2, ...)."""
    node_counter = 1
    for node in t.traverse("levelorder"):
        if not node.is_leaf() and not node.name:
            node.name = f"N{node_counter}"
            node_counter += 1
    return t

# --- Funciones para dividir el árbol (SM1) ---
def find_longest_path(t):
    """Encuentra el camino topológico más largo entre dos hojas en un árbol."""
    max_length = 0
    longest_path_leaves = (None, None)
    leaves = list(t.iter_leaves())
    for i in range(len(leaves)):
        for j in range(i + 1, len(leaves)):
            leaf1, leaf2 = leaves[i], leaves[j]
            dist = t.get_distance(leaf1, leaf2, topology_only=True)
            if dist > max_length:
                max_length = dist
                longest_path_leaves = (leaf1, leaf2)
    # Devuelve solo las hojas, ya que la longitud no se usa después
    if longest_path_leaves[0] is not None:
        return longest_path_leaves[0], longest_path_leaves[1]
    return None, None

def total_path(t, leaf1, leaf2):
    """Calcula el camino total entre dos hojas a través de su ancestro común."""
    # Esta es tu implementación original para encontrar el camino.
    ancestor = leaf1.get_common_ancestor(leaf2)
    path_to_ancestor = leaf1.get_ancestors()
    if ancestor not in path_to_ancestor:
        path_to_ancestor.append(ancestor)
    path_from_ancestor = leaf2.get_ancestors()
    if ancestor in path_from_ancestor:
        path_from_ancestor.remove(ancestor)
    
    # Asegura que el camino esté en el orden correcto desde leaf1 a leaf2
    # El camino desde leaf1 al ancestro debe estar en orden inverso (hoja -> raíz)
    path1 = list(reversed(leaf1.get_ancestors()))
    # El camino desde leaf2 al ancestro (raíz -> hoja)
    path2 = leaf2.get_ancestors()
    
    # Encuentra la ruta correcta uniendo los caminos en el ancestro
    common_ancestor = t.get_common_ancestor(leaf1, leaf2)
    path_nodes = []
    # get_ancestors no incluye el nodo mismo, así que lo añadimos
    n1 = leaf1
    while n1 is not common_ancestor:
        path_nodes.append(n1)
        n1 = n1.up
    path_nodes.append(common_ancestor)
    
    path_to_leaf2 = []
    n2 = leaf2
    while n2 is not common_ancestor:
        path_to_leaf2.append(n2)
        n2 = n2.up
    
    # Invertimos el segundo camino y lo añadimos (excluyendo el ancestro duplicado)
    path_nodes.extend(list(reversed(path_to_leaf2)))
    return path_nodes

def find_middle_node(path):
    """Identifica el nodo central de una lista de nodos (un camino)."""
    mid_node_index = len(path) // 2
    # Si la longitud es par, se prefiere el nodo más cercano a la raíz.
    mid_node = path[mid_node_index] if len(path) % 2 != 0 else path[mid_node_index - 1]
    return mid_node

def split_into_clades(t, mid_node):
    """Divide un árbol en dos clados en el nodo central."""
    if mid_node.up is None:
        print("Advertencia: El nodo central es la raíz. La división no es posible.")
        return None, None
    clade1 = mid_node.detach()
    clade2 = t
    return clade1, clade2

# --- Funciones para comparar hermanos (SM1) ---
def compare_siblings(node_b, node_w):
    """Compara si el primer hermano de dos nodos es diferente."""
    siblings_b = node_b.get_sisters()
    siblings_w = node_w.get_sisters()
    sibling_name_b = siblings_b[0].name if siblings_b else None
    sibling_name_w = siblings_w[0].name if siblings_w else None
    return sibling_name_b != sibling_name_w

def select_nodes_sibling_change(clade_b, clade_w):
    """Selecciona nodos de hoja basados en el cambio de hermanos."""
    selected_nodes = []
    # Bucle anidado ineficiente pero es el de tu código original funcional
    for node_b in clade_b.iter_leaves():
        for node_w in clade_w.iter_leaves():
            if node_b.name == node_w.name and compare_siblings(node_b, node_w):
                selected_nodes.append(node_b.name)
    return selected_nodes

# --- Funciones para análisis de objetivo (SM2) ---
def find_subtree_with_target(tree, target_node_name):
    """Encuentra el subárbol más pequeño que contiene el nodo objetivo y sus hermanos."""
    try:
        target_node = tree.search_nodes(name=target_node_name)[0]
        parent = target_node.up
        if parent:
            return set(parent.get_leaf_names())
        return {target_node.name}
    except IndexError:
        return set()

# --- Función de utilidad ---
def clean_set(s):
    """Limpia los nombres de los nodos en un conjunto (quita comillas)."""
    return {item.replace("'", "").replace('"', '') for item in s}


# ==============================================================================
# --- BLOQUE PRINCIPAL DE EJECUCIÓN ---
# ==============================================================================

# --- FASE 1: PREPROCESAMIENTO ---
print("--- Iniciando Preprocesamiento Automático ---")

base_path = "data/"
output_clade_path = os.path.join(base_path, "SM1C1C2_output")
os.makedirs(output_clade_path, exist_ok=True)

categories = ['B2C', 'W2C', 'B4C', 'W4C', 'B8C', 'W8C', 'B16C', 'W16C']
all_clades = {}

for cat in categories:
    print(f"Procesando categoría: {cat}...")
    input_dir = os.path.join(base_path, f"{cat}output")
    original_newick = os.path.join(input_dir, "1-tree.newick")
    named_newick = os.path.join(input_dir, "t2.newick")

    t = Tree(original_newick, format=1)
    t_named = add_internal_node_names(t)
    t_named.write(outfile=named_newick, format=1)

    tree_to_split = Tree(named_newick, format=1)
    
    # --- Lógica de división corregida usando TUS funciones ---
    leaf1, leaf2 = find_longest_path(tree_to_split)
    
    if leaf1 and leaf2:
        path_nodes = total_path(tree_to_split, leaf1, leaf2)
        mid_node = find_middle_node(path_nodes)
        
        # Copiamos el árbol antes de dividirlo porque .detach() lo modifica
        tree_copy_for_split = Tree(named_newick, format=1)
        # Necesitamos encontrar el 'mid_node' en la copia del árbol
        mid_node_in_copy = tree_copy_for_split.search_nodes(name=mid_node.name)[0]
        clade1, clade2 = split_into_clades(tree_copy_for_split, mid_node_in_copy)

        if clade1 and clade2:
            clade1_name, clade2_name = f"C1{cat}", f"C2{cat}"
            all_clades[clade1_name], all_clades[clade2_name] = clade1, clade2
            clade1.write(outfile=os.path.join(output_clade_path, f"{clade1_name}.newick"), format=1)
            clade2.write(outfile=os.path.join(output_clade_path, f"{clade2_name}.newick"), format=1)
            print(f" -> Clados {clade1_name} y {clade2_name} generados.")
        else:
            print(f" -> Advertencia: No se pudieron generar clados para {cat} (nodo central podría ser la raíz).")
    else:
        print(f" -> Advertencia: No se pudo encontrar el camino más largo para {cat}.")

print("\n--- Preprocesamiento completado. ---")


# --- FASE 2: ANÁLISIS SM1 (Sclade) ---
print("\n--- Iniciando Análisis SM1 (Sclade) ---")
congruence_map = {
    '2C': (('C1B2C', 'C1W2C'), ('C2B2C', 'C2W2C')),
    '4C': (('C1B4C', 'C1W4C'), ('C2B4C', 'C2W4C')),
    '8C': (('C1B8C', 'C1W8C'), ('C2B8C', 'C2W8C')),
    '16C': (('C1B16C', 'C1W16C'), ('C2B16C', 'C2W16C')),
}
Sclade = set()
for category, pairs in congruence_map.items():
    s1 = select_nodes_sibling_change(all_clades[pairs[0][0]], all_clades[pairs[0][1]])
    s2 = select_nodes_sibling_change(all_clades[pairs[1][0]], all_clades[pairs[1][1]])
    Sclade.update(s1)
    Sclade.update(s2)
print(f"Resultado SM1 - Sclade (Total: {len(Sclade)})")


# --- FASE 3: ANÁLISIS SM2 (Scriterion) ---
print("\n--- Iniciando Análisis SM2 (Scriterion) ---")
beta = "'ProdutividadeRealizadakgha'"
Scriterion = set()
target_clade_pairs = {
    '2C': [all_clades.get('C1B2C'), all_clades.get('C1W2C')],
    '4C': [all_clades.get('C1B4C'), all_clades.get('C1W4C')],
    '8C': [all_clades.get('C1B8C'), all_clades.get('C1W8C')],
    '16C': [all_clades.get('C1B16C'), all_clades.get('C1W16C')],
}
for category, trees in target_clade_pairs.items():
    for tree in trees:
        if tree: # Verificar que el clado exista
            nodes_in_subtree = find_subtree_with_target(tree, beta)
            Scriterion.update(nodes_in_subtree)
Scriterion.discard(beta)
print(f"Resultado SM2 - Scriterion (Total: {len(Scriterion)})")


# --- FASE 4: ANÁLISIS SM3 (Soclade) ---
print("\n--- Iniciando Análisis SM3 (Soclade) ---")
main_tree_path = os.path.join(base_path, "Main/output/1-tree.newick")
target_leaf = "ProdutividadeRealizadakgha"
Soclade = set()
try:
    t_main = Tree(main_tree_path, quoted_node_names=True)
    t_main.set_outgroup(target_leaf)
    for node in t_main.traverse("levelorder"):
        if node.is_leaf() and node.name != target_leaf:
            Soclade.add(node.name)
    print(f"Resultado SM3 - Soclade (Total: {len(Soclade)})")
except Exception as e:
    print(f"Error en el análisis SM3: {e}")


# --- FASE 5: ANÁLISIS SM4 (Scophenetic) ---
print("\n--- Iniciando Análisis SM4 (Scophenetic) ---")
Scophenetic = set()
try:
    t_main_original = Tree(main_tree_path, quoted_node_names=True)
    all_leaves = t_main_original.get_leaf_names()
    for leaf in all_leaves:
        if leaf != target_leaf:
            Scophenetic.add(leaf)
    print(f"Resultado SM4 - Scophenetic (Total: {len(Scophenetic)})")
except Exception as e:
    print(f"Error en el análisis SM4: {e}")


# --- FASE 6: COMBINACIÓN FINAL (rVP) ---
print("\n--- Calculando el conjunto final de Variables Principales (rVP) ---")
sclade_clean = clean_set(Sclade)
scriterion_clean = clean_set(Scriterion)
soclade_clean = clean_set(Soclade)
scophenetic_clean = clean_set(Scophenetic)

union1 = sclade_clean.union(scriterion_clean)
union2 = soclade_clean.union(scophenetic_clean)
rVP = union1.intersection(union2)

print(f"\n Resultado Final - rVP (Total: {len(rVP)})")
print(sorted(list(rVP)))