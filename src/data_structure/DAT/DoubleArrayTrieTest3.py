'''
Created on 2020年1月15日

@author: lipy
'''
#基于双数组实现前缀树
import numpy as np
import time  
from  HashMapTrie import TrieHashMap, Node
import copy
#这一版需要解决一个问题，即重复遍历词表导致的DAT构件速度太低。
#需要借鉴图的遍历算法，使用一个描述节点是否已经遍历过的数据结构，来辅助遍历过程。
char_id_map = {}
id_char_map = {}
class HashMapTriePlus(TrieHashMap):
    
    def __init__(self, max_word_len):
        self.root_node = Node("", None)
        self.nodes_list = [[] for k in range(max_word_len)]#用来存储还未遍历过的节点
        self.max_word_len = max_word_len
    
    def add_term(self, element_list):
        current_node = self.root_node
        path_to_this = ""
        for depth in range(len(element_list)):
            element = element_list[depth]
            path_to_this += element
            if current_node.children_node_map == None or element not in current_node.children_node_map:
                new_node = Node(element, current_node, path_to_this = path_to_this)
                current_node.add_children_node(new_node)
                self.nodes_list[depth].append(new_node)
            current_node = current_node.children_node_map[element]
            
#         print("叶子节点的父路径", current_node.parent_path, current_node.node_name, element_list)
        current_node.set_as_leaf()
        
#     def get_path(self, node):
#         path_to_this_node = ""
#         current_node = node
#         while current_node.parent_node!=None:
#             path_to_this_node = current_node.parent_node.node_name + path_to_this_node
#             current_node = current_node.parent_node
#         return path_to_this_node
    
    def get_path(self, node):
        return node.path_to_this
    
    def print_all(self):
        for i in range(self.max_word_len):
            nodes_this_depth = self.nodes_list[i]
            for node in nodes_this_depth:
                print(node.node_name, node.if_leaf(), end=' ')
            print()
                
class DoubleArrayTrie():
    
    def __init__(self, max_word_len):
        self.base = [1]
        self.check = [0]
        self.size = 1
        self.max_ascii_id = 0
        self.min_ascii_id = 0
        self.max_word_len = max_word_len
        self.hash_trie = HashMapTriePlus(max_word_len)#辅助的hash字典树
    
    def iter_patterns_first(self, term_list):
        for term in term_list:
            self.hash_trie.add_term(term)
            for char in term:
                if char_id_map[char] > self.max_ascii_id: self.max_ascii_id = char_id_map[char]
                if char_id_map[char] < self.min_ascii_id: self.min_ascii_id = char_id_map[char]
        print("最大的ascii码是", self.max_ascii_id, "最小是", self.min_ascii_id)
        self.resize(self.max_ascii_id)
        
        for term in term_list: self.hash_trie.add_term(term)
#         self.hash_trie.print_all()
                
    def build(self, term_list):
        self.iter_patterns_first(term_list)
        former_base = 0
        for node in self.hash_trie.nodes_list[0]:
            b_index = self.base[former_base] + char_id_map[node.node_name]
#             print('b_index', b_index)
            self.base[b_index] = -1 if node.if_leaf() else 1
            self.check[b_index] = former_base

        for i in range(self.max_word_len):
#             print("这一层的节点个数是", len(self.hash_trie.nodes_list[i]))
            nodes_this_depth = self.hash_trie.nodes_list[i]
            for node in nodes_this_depth:
                path_to_this_node = self.hash_trie.get_path(node)
                former_status = 0
                #执行前面的状态转移过程
                former_status = self.update_stage1(former_status, path_to_this_node)
#                 print('former_status', former_status, self.base[former_status], path_to_this_node)
                self.update(former_status, path_to_this_node, node)
                
            if i==0: break
        indexes = list(range(len(self.base)))
        data = [indexes, self.base, self.check]
        data = np.array(data)
#         print(data)
#         for i in indexes:
#             print(i, self.base[i], self.check[i])
#             print("base", self.base)
#             print("check", self.check)

    #假设一个路径已经添加到了dat中，完成对应的状态转移，然后考虑一个后驱节点
    def update_stage1(self,former_status, parent_path):
        if former_status < 0: former_status = -former_status
        former_base = 0
        for a_char in parent_path:
            former_base = self.base[former_status]
            current_status = former_base + char_id_map[a_char] if former_base>0 else \
                                           -former_base + char_id_map[a_char]
            former_status = current_status#完成状态转换
        return former_status
            
    #考察与node同源的节点的情况
    def update(self, former_status, parent_path, node):
        delta = self.base[former_status]
#         print(delta)
        children_nodes = self.hash_trie.get_children_nodes(parent_path)
        while children_nodes!=False:
            if_clean = True
            for b_char in children_nodes.keys():
                b_index = delta + char_id_map[b_char]
                if b_index >= self.size: self.resize(b_index)
                if self.base[b_index]!=0:
                    if_clean = False
                    break
            if if_clean==True:
                break
            delta += 1
#         if parent_path=="人民":
#             print("###", delta, former_status)
        self.base[former_status] = -delta if self.base[former_status] <0 else delta 
        if children_nodes!=False:
            for b_char in children_nodes.keys():
                b_index = delta + char_id_map[b_char]
                self.base[b_index] = -1 if children_nodes[b_char].if_leaf() else 1
                self.check[b_index] = former_status


    def update_bk(self, former_status, parent_path, node):
        delta = self.base[former_status]
        ori_delta = delta
        if delta < 0: delta = -delta
        current_status = delta + char_id_map[node.node_name]                      
        if current_status >= self.size : self.resize(current_status)
#         print(parent_path, node.if_leaf())
        if parent_path=="人民":
            print("***", current_status, self.base[current_status], parent_path, node.node_name, node.if_leaf())
            print("***", former_status, self.base[former_status], char_id_map[node.node_name] )
           
        if self.base[current_status]==0:#如果当前状态对应的位置是空的，可以直接添加新节点
#             print("空节点", parent_path, node.node_name, current_status, node.if_leaf())
            self.base[current_status] = -1 if node.if_leaf() else 1#叶子结点的状态取值是负的
            self.check[current_status] = former_status#check数组更新
            
#             if parent_path=="人民":
#                 print("***", current_status, self.base[current_status], parent_path, node.node_name, node.if_leaf())
            former_status = current_status#完成状态转换

        else:
# #             if parent_path=="人民":
# #                 print("***", current_status, self.base[current_status], parent_path, node.node_name, node.if_leaf())
#            
            #如果当前位置存储的状态不为空，需要检查待添加节点的子节点是否可以添加。如果子节点们可以添加，则当前位置存储的位移量是可用的。
            children_nodes = self.hash_trie.get_children_nodes(parent_path)
#             if parent_path=="人民":
#                 print("*********************")
#             print(children_nodes)
            while children_nodes!=False:
                if_clean = True
                for b_char in children_nodes.keys():
                    b_index = delta + char_id_map[b_char]
                    if b_index >= self.size :
                        self.resize(b_index)
                    if self.base[b_index]!=0:
                        if_clean = False
                        break
                if if_clean==True:
                    break
                delta += 1
#             if node.if_leaf():
#                 print("叶子节点", node.parent_path, former_status, children_nodes)

            self.base[former_status] = -delta if self.base[former_status] <0 else delta 

#             print(former_status, self.base[former_status], parent_path, node.node_name)
            if children_nodes!=False:
                for b_char in children_nodes.keys():
                    self.base[delta + char_id_map[b_char]] = -1 if children_nodes[b_char].if_leaf() else 1
                    self.check[delta + char_id_map[b_char]] = former_status
#                     if children_nodes[b_char].if_leaf():
#                         print("叶子节点", children_nodes[b_char].parent_path, delta + char_id_map[b_char])
                        
#                     self.base[ori_delta + char_id_map[b_char]] = 0
#                     self.check[ori_delta + char_id_map[b_char]] = 0
            current_status = delta + char_id_map[node.node_name] 
            former_status = current_status
#             if parent_path=="人":
#                 print("*********************")
        return former_status
                      
    def containsKey(self, char_ids_in_term):
        start_status = 0
        for a_char_id in char_ids_in_term:
            former_base = self.base[start_status]
            new_index = former_base + a_char_id if former_base>0 else -former_base + a_char_id
            if self.base[new_index]==0:#如果位置是空的
                return False
            else:
                if self.check[new_index] == start_status:#如果当前节已经收录，不需要插入，开始考虑下一个状态
                    start_status = new_index
                    continue
                else:
                    return False
                start_status = new_index
#         print("判断是否为叶子节点", new_index, self.base[new_index])
        if self.base[new_index] < 0:
            return True
        else:
            return False
        
    def resize(self, new_size):
        self.base += [0] * (new_size - len(self.base) + 1000)
        self.check += [0] * (new_size - len(self.check) + 1000)
        self.size = len(self.check)
        
import pickle
if __name__ == '__main__':
    term_list = list(open(r"e:\work\data\CoreNatureDictionary.txt", 'r', encoding='utf8').readlines())
    term_list = list(map(lambda x: x.split("\t")[0], term_list))
    term_list = term_list[:20000] + ["人民"]
#     term_list = term_list[1650:1690] +term_list[1730:1800] +  ["人民"]
#     print(term_list)
#     term_list = list(filter(lambda x: "人" in x, term_list))
    term_list = list(set(term_list))
#     print(term_list)
    
#     term_list = [ '上上下下',
#                   '上下位', '上下其手', '上下半场', '上下句', '上下学', '上下床', '上下文', '上下浮动', '上下游', '上下班',
#                     '上半叶', '上半场', '上半夜', '上半年', '上半时', '上半晌', '上半期', '上半身',
#                        '上坪村', '上城区', '上堆村', '上塘镇',  '上夜班', 
#                         '上官体', '上官剑', '上官姓',  '上家', '上宾', '上将军',
#                          '人民']


#     term_list = ["大力", "伟大", "伟大人"]
#     term_list = ['人民银行', "人民", "一般人", "一个人来了"]
#     term_list = ["人民二路", "人民", "一人"]
    term_list = sorted(term_list)
    max_len = 1
    for term in term_list:
        if len(term)> max_len: max_len = len(term)
        for a_char in term:
            if a_char not in char_id_map:
                char_id_map[a_char] = len(char_id_map)
            
#     char_id_map = {"哈": 0,"工": 1, "大": 2, "人":3, "民": 4, "力": 5, "量": 6, "伟": 7}
    id_char_map = {v: k for k, v in char_id_map.items()}
    print("词语的最大长度是", max_len)
    dat = DoubleArrayTrie(max_len)
    t1 = time.time()
    dat.build(term_list)
    t2 = time.time()
    print("构建耗时", t2 - t1)
    char_ids_in_term = [char_id_map.get(key, 5862) for key in "人民"]
#     print(char_id_map)
    print("检查DAT的功能", char_ids_in_term, dat.containsKey(char_ids_in_term))
#     
    pickle.dump(dat, open("dat.pkl", 'wb'))
#     dat = pickle.load(open("dat.pkl", 'rb'))
    count = 2000000
    char_ids_in_term = [char_id_map.get(key, 5862) for key in "人民币"]
#     print("char_ids_in_term", char_ids_in_term)
    t1 = time.time()
    for i in range(count):
        dat.containsKey(char_ids_in_term)
    t2 = time.time()
    print("速度是", int(count/(t2 - t1)))
    
    
    