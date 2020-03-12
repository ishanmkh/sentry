from __future__ import absolute_import

from rest_framework.response import Response

from sentry.api.bases.project import ProjectEndpoint, StrictProjectPermission
from sentry.rules import rules
from sentry.rules.actions.notify_event_service import NotifyEventServiceAction
from sentry import features


class ProjectRulesConfigurationEndpoint(ProjectEndpoint):
    permission_classes = (StrictProjectPermission,)

    def get(self, request, project):
        """
        Retrieve the list of configuration options for a given project.
        """

        action_list = []
        condition_list = []

        # TODO: conditions need to be based on actions
        for rule_type, rule_cls in rules:
            node = rule_cls(project)
            context = {"id": node.id, "label": node.label, "enabled": node.is_enabled()}

            if hasattr(node, "form_fields"):
                context["formFields"] = node.form_fields

            if features.has(
                "organizations:issue-alerts-targeting", project.organization
            ) and isinstance(node, NotifyEventServiceAction)
            if rule_type.startswith("condition/"):
                condition_list.append(context)
            elif rule_type.startswith("action/"):
                action_list.append(context)

        context = {"actions": action_list, "conditions": condition_list}

        return Response(context)
