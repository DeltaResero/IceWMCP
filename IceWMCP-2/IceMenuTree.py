#############################################################################
# IceMe
# =====
#
# Copyright 2000-2002, Dirk Moebius <dmoebius@gmx.net> 
# and Mike Hostetler <thehaas@binary.net
#
# This work comes with no warranty regarding its suitability for any purpose.
# The author is not responsible for any damages caused by the use of this
# program.
#############################################################################
########
# With Modifications by Erica Andrews (PhrozenSmoke ['at'] yahoo.com), February-December 2003
# This is a modified version of IceMe 1.0.0 ("IceWMCP Edition"), optimized for IceWM ControlPanel.
# Copyright (c) 2003 Erica Andrews
########

#############################
#  PyGtk-2 Port Started By: 
#  	David Moore (djm6202@yahoo.co.nz)
#	March 2003
#############################
#############################
#  PyGtk-2 Port Continued By: 
#	Erica Andrews
#  	PhrozenSmoke ['at'] yahoo.com
#	October/November 2003
#############################

from DndCTree import DndCTree
from MenuParser import *
from constants import *

#set translation support
from icewmcp_common import *

def _(somestr):
	return to_utf8(translateME(somestr))


class IceMenuTree(DndCTree):

    def __init__(self, app):
        DndCTree.__init__(self, 2, 0, [_("Menu"), _("Command")])
        self.app = app
        self.set_selection_mode(SELECTION_BROWSE)
	self.set_spacing(5)  # added 4.3.2003, Erica Andrews 
	self.set_row_height(23)  # added 4.3.2003, Erica Andrews 
        self.column_titles_passive()
        self.connect("tree-expand", self.on_tree_expand)


    def on_tree_expand(self, tree, node):
        for i in range(0,2):
            opt = self.optimal_column_width(i)
	    if i==1: opt=opt+200  # changed 4.3.2003 - Erica Andrews, to make 2nd column slightly wider
            self.set_column_min_width(i, opt)


    def init(self, menufile = None, programsfile = None, toolbarfile = None):
        self.clear()
        self.freeze()
        # insert root node:
        root = self.__insertNode(None, None, MENUTREE_SUBMENU,
                                 "", "$ice_me_icewm$", None, TRUE)
        self.expand(root)
        # insert main menu:
        if menufile:
            m = MenuParser(menufile)
            self.__insertMenu(root, m)
        # insert separator:
        self.__insertSep(root, None, TRUE)
        # insert programs menu:
        node = self.__insertNode(root, None, MENUTREE_SUBMENU,
                                 _("Programs"), "folder", None, TRUE)
        if programsfile:
            m = MenuParser(programsfile)
            self.__insertMenu(node, m)
        # insert separator:
        self.__insertSep(None, None, TRUE)
        # insert toolbar menu:
        node = self.__insertNode(None, None, MENUTREE_SUBMENU,
                                 _("Toolbar"), "folder", None, TRUE)
        if toolbarfile:
            m = MenuParser(toolbarfile)
            self.__insertMenu(node, m)
        # insert separator:
        self.__insertSep(None, None, TRUE)
        # insert special clipboard menu:
        self.clipboard = self.__insertNode(None, None, MENUTREE_SUBMENU,
                                           _("Clipboard"), "$ice_me_clipboard$",
                                           None, TRUE)
        self.columns_autosize()
        self.thaw()
        return root


    def __insertMenu(self, parent, menuparser):
        parent_stack = [parent, ]
        while 1:
            entry = menuparser.getNextEntry()
            if entry is None:
                break
            if entry[0] == MENUTREE_UNKNOWN:
                continue
            if entry[0] == MENUTREE_SUBMENU_END:
                parent_stack.pop()
                parent = parent_stack[-1]
            else:
                params = (parent, None) + tuple(entry)
                node = apply(self.__insertNode, params)
                if entry[0] == MENUTREE_SUBMENU:
                    parent = node
                    parent_stack.append(parent)


    def __insertSep(self, parent, sibling, inactive = FALSE):
        return self.__insertNode(parent, sibling, MENUTREE_SEPARATOR,
                                 "", None, None, inactive)


    def __insertNode(self, parent, sibling,
                     type, text, iconname, command,
                     inactive = FALSE):
        if type not in (MENUTREE_PROG, MENUTREE_RESTART):
            command = ""
        if type == MENUTREE_SEPARATOR:
            text = SEP_STRING
            pix = mask = iconname = None
        else:
            dummy, pix, mask = self.app.getCachedIcon(iconname)
        is_leaf = (type != MENUTREE_SUBMENU)
        # insert node:
        node = self.insert_node(parent, sibling, [text, command], 5,
                                pix, mask, pix, mask, is_leaf)
        # store additional data: iconname, whether it's a restart button
        # and whether the entry is inactive:
        self.node_set_row_data(node, [iconname, type, inactive])
        return node


    def insertNode(self, node, type, text, iconname, command):
        "Insert a new entry under node 'node'."
        if self.isInactive(node):
            parent = node
            self.expand(parent)
            if node.children:
                sibling = node.children[0]
            else:
                sibling = None
        else:
            parent = node.parent
            sibling = node.sibling
        return self.__insertNode(parent, sibling, type, text, iconname, command)


    def getNodeName(self, node):
        return self.__getNodeText(node, 0)

    def getNodeCommand(self, node):
        return self.__getNodeText(node, 1)

    def __getNodeText(self, node, col):
        cell_type = self.node_get_cell_type(node, col)
        if cell_type == CELL_TEXT:
            return self.node_get_text(node, col)
        elif cell_type == CELL_PIXTEXT:
            return self.node_get_pixtext(node, col)[0]
        return ""

    def setNodeName(self, node, name):
        self.__setNodeText(node, name, 0)

    def setNodeCommand(self, node, name):
        self.__setNodeText(node, name, 1)

    def __setNodeText(self, node, name, col):
        cell_type = self.node_get_cell_type(node, col)
        if cell_type == CELL_TEXT:
            self.node_set_text(node, col, name)
        elif cell_type == CELL_PIXTEXT:
            old_text, sp, pix, mask = self.node_get_pixtext(node, col)
            if pix == None:
                self.node_set_text(node, col, name)
            else:
		try:
                	self.node_set_pixtext(node, col, name, sp, pix, mask)
		except:
			pass

    def getNodeIcon(self, node):
        cell_type = self.node_get_cell_type(node, 0)
        if cell_type == CELL_PIXTEXT:
            text, sp, pix, mask = self.node_get_pixtext(node, 0)
            return (pix, mask)
        elif cell_type == CELL_PIXMAP:
            return self.node_get_pixmap(node, 0)
        else:
            return (None, None)

    def setNodeIcon(self, node, pix, mask):
     try:
        cell_type = self.node_get_cell_type(node, 0)
        if cell_type == CELL_PIXTEXT:
            text, sp, old_pix, old_mask = self.node_get_pixtext(node, 0)
	    self.node_set_pixtext(node, 0, text, sp, pix, mask)
        elif cell_type == CELL_PIXMAP:
            self.node_set_pixmap(node, 0, pix, mask)
     except:
	pass

    def getNodeUpperSibling(self, node):
        """In contrast to node.sibling, this function returns the node
        _above_ the current node.

        Returns None, if there is no node above the current node in the
        same level.
        This function is really missing in pygtk.
        """
        if node.parent is None:
            nodes = self.base_nodes()
        else:
            nodes = node.parent.children
        upper_sibling = None
        for n in nodes:
            if n == node:
                return upper_sibling
            upper_sibling = n
        return None

    def isSeparator(self, node):
        return self.getNodeType(node) == MENUTREE_SEPARATOR

    def isInactive(self, node):
        return self.node_get_row_data(node)[2]

    def getNodeType(self, node):
        return self.node_get_row_data(node)[1]

    def setNodeType(self, node, type):
        self.node_get_row_data(node)[1] = type

    def getNodeIconName(self, node):
        return self.node_get_row_data(node)[0]

    def setNodeIconName(self, node, iconname):
        self.node_get_row_data(node)[0] = iconname

    def getMainMenuNode(self):
        # the main menu node is always the first root node
        return self.base_nodes()[0]

    def getProgramsNode(self):
        # the programs node is always the last child of the
        # first root node (the "IceWM" node)
        return self.base_nodes()[0].children[-1]

    def getToolbarNode(self):
        # the toolbar node is always the third root node
        return self.base_nodes()[2]

    def isOnClipboard(self, node):
        "Check whether the node is currently on the clipboard."
        return self.is_ancestor(self.clipboard, node)

    def canMoveUp(self, node):
        "Check whether the node can be moved up in the current subtree."
        upper_sibling = self.getNodeUpperSibling(node)
        if upper_sibling is None: return 0
        return not self.isInactive(upper_sibling)

    def canMoveDown(self, node):
        "Check whether the node can be moved down in the current subtree."
        if node.sibling is None: return 0
        return not self.isInactive(node.sibling)

    def canDelete(self, node):
        "Check whether the node may be deleted."
        return not self.isInactive(node)

    def canInsertOn(self, node):
        "Check whether something may be inserted below/after the node."
        # insert is allowed if the node is not an inactive separator
        return not (self.isInactive(node) and self.isSeparator(node))

    def move_is_permitted(self, source_node, target_node,
                          new_parent, new_sibling):
        """Check whether source_node may be moved via drag and drop to the
        new location at target_node, ie.: position (new_parent,new_sibling)"""
        return self.canDelete(source_node) and self.canInsertOn(target_node)

    def cut(self, node):
        if not self.canDelete(node) or self.isOnClipboard(node):
            gdk_beep()
            return
        # empty the current contents of the clipboard:
        if self.clipboard.children:
            for c in self.clipboard.children:
                self.remove_node(c)
        # move node to the clibboard:
        self.move(node, self.clipboard, None)

    def copy(self, node):
        if self.isOnClipboard(node):
            gdk_beep()
            return
        # empty the current contents of the clipboard:
        if self.clipboard.children:
            for c in self.clipboard.children:
                self.remove_node(c)
        # copy node and decessors recursively to the clipboard:
        self.freeze()
        self.__copy_recursive(self.clipboard, node, 1)
        self.thaw()

    def paste(self, node):
        if not self.clipboard.children:
            # the clipboard is empty
            gdk_beep()
            return
        if not self.canInsertOn(node) or self.isOnClipboard(node):
            # contents of clipboard may not be copied to the node:
            gdk_beep()
            return
        self.freeze()
        self.__copy_recursive(node, self.clipboard.children[0])
        self.thaw()

    def delete(self, node):
        if not self.canDelete(node):
            gdk_beep()
            return
        self.remove_node(node)

    def hasPasteData(self):
        return len(self.clipboard.children)

    def __copy_recursive(self, target_node,
                         source_node, as_child=0):
        if self.isInactive(target_node) or as_child:
            parent = target_node
            self.expand(parent)
            if target_node.children:
                sibling = target_node.children[0]
            else:
                sibling = None
        else:
            parent = target_node.parent
            sibling = target_node.sibling

        new_node = self.__insertNode(parent, sibling,
                                     self.getNodeType(source_node),
                                     self.getNodeName(source_node),
                                     self.getNodeIconName(source_node),
                                     self.getNodeCommand(source_node))

        if not source_node.is_leaf:
            for c in source_node.children:
                self.__copy_recursive(new_node, c, 1)

