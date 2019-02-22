import com.intellij.openapi.actionSystem.ActionManager;
import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.actionSystem.PlatformDataKeys;
import com.intellij.openapi.editor.Editor;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.ui.Messages;
import com.intellij.openapi.vfs.VirtualFile;
import com.intellij.openapi.startup.StartupManager;
import org.jetbrains.annotations.SystemIndependent;

public class HelloWorldAction extends AnAction {

    @Override
    public void actionPerformed(AnActionEvent e) {

        Project project = e.getData(PlatformDataKeys.PROJECT);

        ActionManager actionManager = e.getActionManager();


        @SystemIndependent String basePath = project.getBasePath();
        VirtualFile projectFile = project.getProjectFile();
        @SystemIndependent String projectFilePath = project.getProjectFilePath();

        System.out.println("basePath:" + basePath);
        System.out.println("projectFile:" + projectFile);
        System.out.println("projectFilePath:" + projectFilePath);


        String title = "标题";
        String msg = "2018,起航";

        Messages.showMessageDialog(project, msg, title, Messages.getInformationIcon());
    }
}