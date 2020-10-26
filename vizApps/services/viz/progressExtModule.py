import param
import panel as pn
from contextlib import contextmanager

class ProgressExtMod(param.Parameterized):
    completed = param.Integer(default=0)
    bar_color = param.String(default="info")
    num_tasks = param.Integer(default=100, bounds=(1, None))

    # @param.depends('completed', 'num_tasks')
    @property
    def value(self) -> int:
        """Returs the progress value
        Returns:
            int: The progress value
        """
        return int(100 * (self.completed / self.num_tasks))

    def reset(self):
        """Resets the value and message"""
        # Please note the order matters as the Widgets updates two times. One for each change
        self.completed = 0

    @param.depends("completed", "message", "bar_color")
    def view(self):
        """View the widget
        Returns:
            pn.viewable.Viewable: Add this to your app to see the progress reported
        """
        if self.value:
            #return pn.Row(pn.pane.HTML(str(self.value)) ,pn.widgets.Progress())
            return pn.widgets.Progress(active=True, value=self.value, align="center", sizing_mode="stretch_width", height=5)
        return None

    @contextmanager
    def increment(self):
        """Increment the value
        Can be used as context manager or decorator?
        Yields:
            None: Nothing is yielded
        """
        self.completed += 1
        yield
        if self.completed == self.num_tasks:
            self.reset()

