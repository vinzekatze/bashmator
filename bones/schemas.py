main_schema = '''
type: object
properties:
  author:
    type: 
      - string
      - 'null'
  description:
    type: 
      - string
      - 'null'
  tags:
    type: 
      - array
      - 'null'
    items:
      type:
        - string
        - number
  install:
    type: 
      - string
      - 'null'
  arguments:
    type: 
      - object
      - 'null'
    patternProperties:
      ^[A-Za-z][A-Za-z0-9_-]*$:
        type: object
        properties:
          default:
            type:
              - 'null'
              - string
              - number
              - array
            items:
              type:
                - string
                - number
          replacer: 
            type: string
          description:
            type: 
              - string
              - 'null'
        required:
          - default
          - replacer
          - description
        additionalProperties: false
    additionalProperties: false
  shell:
    type: string
  script:
    type:
      - string
      - 'null' 
required:
  - description
  - author
  - tags
  - install
  - arguments
  - shell
  - script
patternProperties:
  ^item_[1-9][0-9]*$:
    type:
      - object
    properties:
      description:
        type: 
          - string
          - 'null'
      script:
        type:
          - string
          - 'null'
    required:
      - description
      - script
    additionalProperties: false
additionalProperties: false
'''

help_yaml_structure='''
description:      <string or null>
author:           <string or null>
tags:             <list or null> 
  - [tag]         <string or number>     
  - [...]
install:          <string or null> 
arguments:        <dictionary or null>
  [argument name]:
    default:      <string, number, list or null>
    replacer:     <string>
    description:  <string or null>
  [...]
shell:            <string>
script:           <string or null>
item_[NUM]:                             (not required)
  script:         <string or null>
  description:    <string or null>
item_[...]
'''