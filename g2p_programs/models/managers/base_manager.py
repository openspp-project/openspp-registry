# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.tools import safe_eval


class BaseManager(models.AbstractModel):
    _name = "base.programs.manager"
    _description = "Base Manager"

    def _get_eval_context(self):
        """Prepare the context used when evaluating python code
        :returns: dict -- evaluation context given to safe_eval
        """
        return {
            "datetime": safe_eval.datetime,
            "dateutil": safe_eval.dateutil,
            "time": safe_eval.time,
            "uid": self.env.uid,
            "user": self.env.user,
        }

    def _safe_eval(self, string, locals_dict=None):
        """Evaluates a string containing a Python expression.
        :param string: string expression to be evaluated
        :param locals_dict: local variables for evaluation
        :returns: the result of the evaluation
        """
        return safe_eval.safe_eval(string, self._get_eval_context(), locals_dict)
