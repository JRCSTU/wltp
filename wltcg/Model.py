'''
Created on 26 Dec 2013

@author: ankostis
'''

class Model(object):
    '''
    Describes and validates the vehicle and cycle data for running WLTC.
    '''


    def __init__(self, model_json):
        import jsonschema
        from textwrap import dedent

        self.schema = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'title': 'Json-schema describing the vehicle attributes used to generate WLTC gear-shifts profile.',
            'type': 'object',
            'properties': {
               'mass': {
                   '$ref': '#/definitions/positiveInteger',
                   'title': 'vehicle mass',
                   'description': 'The test mass of the vehicle in kg.',
                },
               'p_rated': {
                   '$ref': '#/definitions/positiveInteger',
                   'title': 'maximum rated power',
                   'description': 'The maximum rated engine power as declared by the manufacturer.',
               },
               'n_rated': {
                   '$ref': '#/definitions/positiveInteger',
                   'title': 'rated engine speed',
                   'description': dedent('''
                       The rated engine speed at which an engine develops its maximum power.
                       If the maximum power is developed over an engine speed range,
                       it is determined by the mean of this range.
                       This is called 's' in the specs.
                   '''),
                },
               'n_idle': {
                   '$ref': '#/definitions/positiveInteger',
                   'title': 'idling speed',
                   'description': 'The idling speed as defined of Annex 1.',
                },
               'n_min': {
                   '$ref': '#/definitions/positiveInteger',
                   'title': 'minimum engine speed',
                   'description': dedent('''
                    minimum engine speed for gears > 2 when the vehicle is in motion. The minimum value
                    is determined by the following equation:
                        n_min = n_idle + 0.125 * (n_rated - n_idle)
                    Higher values may be used if requested by the manufacturer.
                   '''),
                },
               'gear_ratios': {
                   '$ref': '#/definitions/positiveIntegers',
                   'title': 'gear ratios',
                   'description':
                   'An array with the gear-ratios obtained by dividing engine-revolutions (1/min) by vehicle-speed (km/h).',
                },
               'resistance_coeffs': {
                   '$ref': '#/definitions/positiveIntegers',
                   'title': 'driving resistance coefficients',
                   'description': 'The 3 driving resistance coefficients f0, f1, f2 as defined in Annex 4, in N, N/(km/h), and N/(km/h)² respectively.',
                },
               'full_load_curve': {
                   'type': 'array',
                   'items': { 'type': 'number'},
                   'maxItems': 100,
                   'minItems': 100,
                   'title': 'full load power curve',
                   'description': dedent('''
                        The values for the full load power curve, normalised (1 to 100) for
                        the rated power and (n_rated – n_idle):
                            p_wot(n_norm) / p_rated
                        where:
                            n_norm = (n - n_idle) / (n_rated  - n_idle)
                   '''),
                },
            }, # props
            'required': ['mass', 'p_rated', 'n_rated', 'n_idle', 'gear_ratios', 'resistance_coeffs'],
            'definitions': {
                'positiveInteger': {
                    'type': 'integer',
                    'minimum': 0,
                    'exclusiveMinimum': True,
                },
                'positiveIntegers': {
                    'type': 'array',
                   'items': { '$ref': '#/definitions/positiveInteger' },
                },
            }
        }

        jsonschema.validate(model_json, self.schema)


