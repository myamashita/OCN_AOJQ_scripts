# -*- coding: utf-8 -*-
import inspect
# First import the embed function
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.config.loader import Config

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
        prompt_config = cfg.PromptManager
        prompt_config.in_template = 'Debug.In <\\#>: '
        prompt_config.in2_template = '   .\\D.: '
        prompt_config.out_template = 'Debug.Out<\\#>: '

        # Messages displayed when I drop into and exit the shell.
        banner_msg = ("\n**Embended Interpreter:\n"
                      "Hit Ctrl-D to exit interpreter and continue program.\n"
                      "Note that if you use %kill_embedded, you can fully deactivate\n"
                      "This embedded instance so it will never turn on again")
        exit_msg = '**Leaving Embended Interpreter'
        ipshell = InteractiveShellEmbed(config=cfg, banner1=banner_msg,
                                        exit_msg=exit_msg)

        frame = inspect.currentframe().f_back
        msg = 'Debuging at {0.f_code.co_filename} at line {0.f_lineno}'.format(frame)

        # Go back one level! 
        # This is needed because the call to ipshell is inside the function ipsh()
        ipshell(msg, stack_depth=2)
