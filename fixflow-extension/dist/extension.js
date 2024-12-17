"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
const http = __importStar(require("http"));
const url = __importStar(require("url"));
function activate(context) {
    const server = http.createServer(async (req, res) => {
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
        if (req.method === 'OPTIONS') {
            res.writeHead(200);
            res.end();
            return;
        }
        const parsedUrl = url.parse(req.url || '', true);
        const command = parsedUrl.pathname?.substring(1);
        const queryParams = parsedUrl.query;
        console.log('Received command:', command, 'with params:', queryParams);
        try {
            switch (command) {
                case 'nextTab':
                    await vscode.commands.executeCommand('workbench.action.nextEditor');
                    break;
                case 'previousTab':
                    await vscode.commands.executeCommand('workbench.action.previousEditor');
                    break;
                case 'closeTab':
                    await vscode.commands.executeCommand('workbench.action.closeActiveEditor');
                    break;
                case 'closeAllTabs':
                    await vscode.commands.executeCommand('workbench.action.closeAllEditors');
                    break;
                case 'closeTabsToRight':
                    await vscode.commands.executeCommand('workbench.action.closeEditorsToTheRight');
                    break;
                case 'goToLine':
                    const line = parseInt(queryParams.line);
                    if (isNaN(line)) {
                        throw new Error('Line number must be provided as a query parameter');
                    }
                    const editor = vscode.window.activeTextEditor;
                    if (editor) {
                        const position = new vscode.Position(line - 1, 0);
                        editor.selection = new vscode.Selection(position, position);
                        await editor.revealRange(new vscode.Range(position, position), vscode.TextEditorRevealType.InCenter);
                    }
                    break;
                case 'recentFiles':
                    // Get all editor tabs
                    const tabGroups = vscode.window.tabGroups;
                    const allTabs = tabGroups.all.flatMap(group => group.tabs);
                    // Convert tabs to a simplified format
                    const fileList = allTabs
                        .slice(0, 100)
                        .map(tab => ({
                        path: tab.input instanceof vscode.TabInputText ?
                            tab.input.uri.fsPath :
                            undefined,
                        label: tab.label
                    }))
                        .filter(file => file.path); // Only include files with valid paths
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    return res.end(JSON.stringify({
                        status: 'success',
                        command,
                        files: fileList
                    }));
                default:
                    throw new Error('Command not found');
            }
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ status: 'success', command }));
        }
        catch (error) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                status: 'error',
                message: error.message || 'Failed to execute command'
            }));
        }
    });
    server.listen(3001, 'localhost', () => {
        console.log('VS Code extension server is running on http://localhost:3001');
    });
    context.subscriptions.push({
        dispose: () => {
            server.close();
        }
    });
}
exports.activate = activate;
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map