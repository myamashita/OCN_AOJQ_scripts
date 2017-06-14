# -*- coding: utf-8 -*-
#
# To work with the New terminal interface IPython 5.0 ...
#
import inspect
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.terminal.prompts import Prompts, Token
from traitlets.config.loader import Config


class MyPrompt(Prompts):

    def in_prompt_tokens(self, cli=None):
        return [(Token.Prompt, 'Debug <'),
                (Token.PromptNum, str(self.shell.execution_count)),
                (Token.Prompt, '>')]

if __name__ == '__main__':

    def ipsh():
        """
        Start a regular IPython session at any point in your program.

        This allows you to evaluate dynamically the state of your code,
        operate with your variables, analyze them, etc. Note however that
        any changes you make to values while in the shell do not propagate
        back to the running code, so it is safe to modify your values because
        you won’t break your code in bizarre ways by doing so.

        Usage
        _____
        Put ipsh() anywhere in your code where you want it to open.
        This code will load an embeddable IPython shell always with no changes
        for nested embededings.

        Notes
        _____
        + InteractiveShellEmbed instances don't print the standard system
        banner and messages. The IPython banner (which actually may contain
        initialization messages) is available as get_ipython().banner in case
        you want it.

        + InteractiveShellEmbed instances print the following information
        everytime they start:
        - A global startup banner.
        - A call-specific header string, which you can use to indicate where
        in the execution flow the shell is starting.

        + They also print an exit message every time they exit.

        + Both the startup banner and the exit message default to None, and can
        be set either at the instance constructor or at any other time with the
        by setting the banner and exit_msg attributes.

        + The shell instance can be also put in 'dummy' mode globally or on a
        per-call basis. This gives you fine control for debugging without having
        to change code all over the place.

        """
        # Configure the prompt so that I know I am in a nested (embedded) shell
        cfg = Config()
        cfg.TerminalInteractiveShell.prompts_class = MyPrompt

        # Messages displayed when I drop into and exit the shell.
        banner_msg = ("\n**Dropping into Embended Interpreter:\n"
                      "Hit Ctrl-D to exit interpreter and continue program.\n")
        exit_msg = '**Leaving Embended Interpreter, back to program'
        ipshell = InteractiveShellEmbed(config=cfg, banner1=banner_msg,
                                        exit_msg=exit_msg)

        frame = inspect.currentframe().f_back
        msg = 'Debuging at line {0.f_lineno}'.format(frame)
        # Go back one level!
        # This is needed because the call to ipshell is
        # inside the function ipsh()
        ipshell(msg, stack_depth=2)
