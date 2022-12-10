import argparse
import i3ipc
import json
import graphviz
import pprint

from collections import deque


class Visualizer:
    def __init__(self):
        i3 = i3ipc.Connection()
        self.root = i3.get_tree()

    def visualize(self, workspace='focused', verbose=0, filename='output'):
        if workspace == 'focused':
            self.visualize_container(self.root.find_focused().workspace(), filename=filename, verbose=verbose)
        elif workspace == 'visible':
            pass
        elif workspace == 'all':
            self.visualize_container(self.root, filename=filename, verbose=verbose)

    def visualize_container(self, con, filename, verbose):
        g = graphviz.Digraph(name=filename)
        g.attr('node', shape='box')

        q = deque([con])
        while q:
            for _ in range(len(q)):
                curr = q.popleft()
                g.node(str(curr.id), label=self.get_con_label(curr, verbose))

                for node in curr.nodes:
                    g.edge(str(curr.id), str(node.id))
                    q.append(node)

        g.render(format='pdf')

    def get_con_label(self, con, verbose):
        ipc_data = con.ipc_data
        ipc_data.pop('nodes')

        if verbose == 1:
            # Show the nested dict but maybe in the same line
            label = pprint.pformat(ipc_data, sort_dicts=False)
        elif verbose == 2:
            # Show the nested dict in separate lines
            label = json.dumps(ipc_data, indent=2)
        else:
            # Ignore key value pair in nested dict
            label = pprint.pformat(ipc_data, depth=1, sort_dicts=False)

        return label


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-w', '--workspace', default='focused', type=str,
                        help='Which workspace to visualize.')
    parser.add_argument('-v', '--verbose', default=0, type=int,
                        help='Logging level of the node content.')
    parser.add_argument('-f', '--filename', default='output', type=str,
                        help='Filename of the output dot file and pdf file.')
    args = parser.parse_args()

    visualizer = Visualizer()
    visualizer.visualize(workspace=args.workspace, verbose=args.verbose, filename=args.filename)
