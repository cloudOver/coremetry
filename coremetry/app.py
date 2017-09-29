MODULE = {
    'api': [
        'coremetry.views.api',
    ],
    'models': [
        'coremetry.models.coremetry',
    ]
    'hooks': {
        'cron.minute': ['coremetry.hooks.monitor'],
    },
}
