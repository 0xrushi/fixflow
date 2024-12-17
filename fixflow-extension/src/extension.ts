import * as vscode from "vscode";
import * as http from "http";
import * as url from "url";
import * as path from "path";

export function activate(context: vscode.ExtensionContext) {
  const server = http.createServer(async (req, res) => {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");

    if (req.method === "OPTIONS") {
      res.writeHead(200);
      res.end();
      return;
    }

    const parsedUrl = url.parse(req.url || "", true);
    // Remove leading slash and convert to lowercase for consistent comparison
    const command = parsedUrl.pathname?.substring(1).toLowerCase();
    const queryParams = parsedUrl.query;

    console.log("Received command:", command, "with params:", queryParams);

    try {
      switch (command) {
        case "nexttab":
          await vscode.commands.executeCommand("workbench.action.nextEditor");
          break;

        case "previoustab":
          await vscode.commands.executeCommand(
            "workbench.action.previousEditor"
          );
          break;

        case "closetab":
          await vscode.commands.executeCommand(
            "workbench.action.closeActiveEditor"
          );
          break;

        case "closealltabs":
          await vscode.commands.executeCommand(
            "workbench.action.closeAllEditors"
          );
          break;

        case "closetabstoright":
          await vscode.commands.executeCommand(
            "workbench.action.closeEditorsToTheRight"
          );
          break;

        case "openfile":
          console.log("Processing openFile command...");
          const filePath = queryParams.path as string;
          if (!filePath) {
            throw new Error("File path must be provided as a query parameter");
          }

          console.log("Attempting to open file:", filePath);
          // Handle both absolute and workspace-relative paths
          let fileUri;
          if (path.isAbsolute(filePath)) {
            fileUri = vscode.Uri.file(filePath);
          } else {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (!workspaceFolders) {
              throw new Error("No workspace folder is open");
            }
            fileUri = vscode.Uri.joinPath(workspaceFolders[0].uri, filePath);
          }

          console.log("Opening file with URI:", fileUri.fsPath);
          const document = await vscode.workspace.openTextDocument(fileUri);
          await vscode.window.showTextDocument(document);
          break;

        case "listopentabs":
          const tabs = vscode.window.tabGroups.all.flatMap((group, index) =>
            group.tabs.map((tab) => ({
              groupIndex: index,
              isActive: tab.isActive,
              label: tab.label,
              path:
                tab.input instanceof vscode.TabInputText
                  ? tab.input.uri.fsPath
                  : undefined,
            }))
          );

          res.writeHead(200, { "Content-Type": "application/json" });
          return res.end(
            JSON.stringify({
              status: "success",
              command,
              tabs,
            })
          );

        case "gototabname":
          const tabName = queryParams.name as string;
          if (!tabName) {
            throw new Error("Tab name must be provided as a query parameter");
          }

          const allTabs = vscode.window.tabGroups.all.flatMap(
            (group) => group.tabs
          );
          const targetTab = allTabs.find((tab) => tab.label === tabName);

          if (!targetTab) {
            throw new Error(`No tab found with name: ${tabName}`);
          }

          if (targetTab.input instanceof vscode.TabInputText) {
            const doc = await vscode.workspace.openTextDocument(
              targetTab.input.uri
            );
            await vscode.window.showTextDocument(doc);
          }
          break;

        case "gotoline":
          const line = parseInt(queryParams.line as string);
          if (isNaN(line)) {
            throw new Error(
              "Line number must be provided as a query parameter"
            );
          }
          const editor = vscode.window.activeTextEditor;
          if (editor) {
            const position = new vscode.Position(line - 1, 0);
            editor.selection = new vscode.Selection(position, position);
            await editor.revealRange(
              new vscode.Range(position, position),
              vscode.TextEditorRevealType.InCenter
            );
          }
          break;

        case "recentfiles":
          const tabGroups = vscode.window.tabGroups;
          const allRecentTabs = tabGroups.all.flatMap((group) => group.tabs);

          const fileList = allRecentTabs
            .slice(0, 100)
            .map((tab) => ({
              path:
                tab.input instanceof vscode.TabInputText
                  ? tab.input.uri.fsPath
                  : undefined,
              label: tab.label,
            }))
            .filter((file) => file.path);

          res.writeHead(200, { "Content-Type": "application/json" });
          return res.end(
            JSON.stringify({
              status: "success",
              command,
              files: fileList,
            })
          );

        default:
          console.log("Command not recognized:", command);
          throw new Error("Command not found");
      }

      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ status: "success", command }));
    } catch (error: any) {
      console.error("Error processing command:", error);
      res.writeHead(500, { "Content-Type": "application/json" });
      res.end(
        JSON.stringify({
          status: "error",
          command,
          message: error.message || "Failed to execute command",
        })
      );
    }
  });

  server.listen(3068, "localhost", () => {
    console.log("VS Code extension server is running on http://localhost:3068");
  });

  context.subscriptions.push({
    dispose: () => {
      server.close();
    },
  });
}

export function deactivate() {}
