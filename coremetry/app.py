MODULE = {
    'api': [
        'coremetry.views.api',
    ],
    'models': [
        'coremetry.models.coremetry',
    ],
    'hooks': {
        'cron.minute': ['coremetry.hooks.monitor', ],
        'agent.vm.remove_vm': ['coremetry.hooks.vm', ],
    },
}
