main_schema = '''
type: object
properties:
  author:
    type: 
      - string
      - 'null'
  info:
    type: 
      - string
      - 'null'
  tags:
    type: 
      - array
      - 'null'
  install:
    type: 
      - string
      - 'null'
  variables:
    type: 
      - object
      - 'null'
  shell:
    type: string
  script:
    type: string
required:
  - author
  - info
  - tags
  - install
  - variables
  - shell
  - script
additionalProperties: false
'''

variables_schema = '''
type: object
properties:
  default:
    type:
      - 'null'
      - string
      - number
      - array
  replacer: 
    type: string
  info:
    type: 
      - string
      - 'null'
required:
  - default
  - replacer
  - info
additionalProperties: false
'''