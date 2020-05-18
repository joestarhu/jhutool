#! /usr/bin/env python3
import os
import re

basedir = os.path.abspath(os.path.dirname(__file__))
f_path = basedir + '/static/axure/'

rootNodes = 'rootNodes'
pageName = 'pageName'
url = 'url'
children = 'children'


class Axure:
    def __init__(self, id):
        path = f_path + str(id) + '/data/document.js'
        with open(path, 'r') as f:
            docjs_msg = f.read()
        self.cfg_set(docjs_msg)
        self.tree_str_set(docjs_msg)
        self.tree = self.tree_bulid(self.tree_msg)

        html_lst = []
        for k in self.cfg:
            html = re.findall('.*\.html', self.cfg[k])
            if html:
                html_lst.append(html[0][:-5])
        self.html_lst = html_lst

    def cfg_set(self, docjs_msg):
        """
        获取data/document.js中的配置项
        """
        rule = '[a-zA-Z]+\s*=\s*".*?"'
        content = re.findall(rule, docjs_msg)
        d = {}
        for line in content:
            kv = line.split('=')
            k = kv[0]
            v = kv[1][1:-1]
            d[k] = v
        self.cfg = d

    def struct_idx(self, msg, start='(', end=')'):
        cnt = s_id = e_id = 0
        lst = []
        for idx in range(len(msg)):
            if msg[idx] == start:
                if cnt == 0:
                    s_id = idx
                cnt += 1
            if msg[idx] == end:
                cnt -= 1
                if cnt == 0:
                    e_id = idx
                    lst.append((s_id, e_id))
        return lst

    def tree_str_set(self, docjs_msg):
        d = self.cfg
        for k in d:
            if d[k] == rootNodes:
                break
        start = k
        rule = f'_\({start}.*\),'
        content = re.findall(rule, docjs_msg)
        tree_msg = content[0].replace('_', '')
        s_id, e_id = self.struct_idx(tree_msg)[0]
        self.tree_msg = tree_msg[s_id + 4:e_id - 1]

    def tree_bulid(self, msg, tree=None):
        tree = tree or []
        lst = self.struct_idx(msg)
        for s, e in lst:
            print(msg[s:e+1])
            # 把前后的()都给移除掉
            tree.append(self.node_create(msg[s+1:e]))
        return tree

    def node_create(self, msg):
        """
        构建Axure的节点信息
        """
        node = {}
        d = self.cfg
        msg = msg.split(',')
        for i in range(len(msg)):
            val = msg[i]
            if d.get(val, val) in [pageName, url]:
                node[d[val]] = d[msg[i + 1]]
        return node


if __name__ == '__main__':
    a = Axure(2)
    print(a.tree)
    # print(a.tree_msg)
    #print(a.cfg)
    # print(a.html_lst)
