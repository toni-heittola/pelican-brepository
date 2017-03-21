Pelican-brepository - File repository for Pelican
=================================================

`pelican-brepository` is an open source Pelican plugin to produce personnel listings from yaml data structures. The plugin is developed to be used with Markdown content and Bootstrap 3 based template.

**Author**

Toni Heittola (toni.heittola@gmail.com), [GitHub](https://github.com/toni-heittola), [Home page](http://www.cs.tut.fi/~heittolt/)

Installation instructions
=========================

## Requirements

**bs4** is required. To ensure that all external modules are installed, run:

    pip install -r requirements.txt

**bs4** (BeautifulSoup) for parsing HTML content

    pip install beautifulsoup4

## Pelican installation

Make sure you include [Bootstrap](http://getbootstrap.com/) in your template.

Make sure the directory where the plugin was installed is set in `pelicanconf.py`. For example if you installed in `plugins/pelican-brepository`, add:

    PLUGIN_PATHS = ['plugins']

Enable `pelican-brepository` with:

    PLUGINS = ['pelican-brepository']

Insert personnel list or panel into the page template:

    {% if page.brepository %}
        {{ page.brepository }}
    {% endif %}

Insert personnel list or panel into the article template:

    {% if article.brepository %}
        {{ article.brepository }}
    {% endif %}

Usage
=====

Personnel listing generation is triggered for the page either by setting BPERSONNEL metadata for the content (page or article) or using `<div>` with class `brepository` or `brepository-item`.

Layouts

- **brepository**, repository listing  
- **brepository-item**, individual repository item information card

There is two layout modes available for both of these: `panel` and `list`.

## Repository registry

Registry has two parts:
    - **`repository`** containing basic information of each repository item
    - **`sets`**, list of items assigned to the set

Example yaml-file:

    repository:
      - name: file1
        title: Test file 1
        url: http://foo.bar/file1.zip
        type: audio
        size: 1.0 GB

      - name: file2
        title: Test file 2
        url: http://foo.bar/file2.zip
        type: python-package
        version: 1.0.1
        package-type: zip    

      - name: file3
        title: Test file 3
        url: http://foo.bar/file3.zip
        type: matlab-package
        version: 1.0.1
        package-type: zip      

      - name: repo1
        title: Test repository
        url: https://github.com/toni-heittola/pelican-btoc
        type: git

      - name: latex-template
        title: Latex template
        url: latex_template.zip
        size: 123 KB
        package-type: zip
        type: latex

      - name: word-template
        title: Word template
        url: word_template.doc
        size: 12 KB
        package-type: doc
        type: word    

    sets:
      file_set1:
        - file1
        - repo1
        - file2

The default templates support following fields:

- name
- title
- url
- type, valid values [audio, git, python-package, matlab-package, latex, word, doc] to add more types use BREPOSITORY_TYPE_ICONS global variable
- version
- package-type
- size
- DOI
- DOI_img

## Parameters

The parameters can be set in global, and content level. Globally set parameters are are first overwritten content meta data, and finally with div parameters.

### Global parameters

Parameters for the plugin can be set in `pelicanconf.py' with following parameters:

| Parameter                 | Type      | Default       | Description  |
|---------------------------|-----------|---------------|--------------|
| BREPOSITORY_SOURCE         | String    |  | YAML-file to contain repository registry, see example format above. |
| BREPOSITORY_TEMPLATE       | Dict of Jinja2 templates |  | Two templates can be set for panel and list  |
| BPERSONNEL_ITEM_TEMPLATE  | Dict of Jinja2 templates |  | Two templates can be set for panel and list  |
| BREPOSITORY_ITEM_CARD_TEMPLATE  | Jinja2 template |  | Template for repository item information card  |
| BREPOSITORY_PANEL_COLOR          | String    | panel-primary |  CSS class used to color the panel template in the default template. Possible values: panel-default, panel-primary, panel-success, panel-info, panel-warning, panel-danger |
| BREPOSITORY_HEADER               | String    | Content       | Header text  |

### Content wise parameters

| Parameter                 | Example value     | Description  |
|---------------------------|-----------|--------------|
| BREPOSITORY                | True      | Enable brepository listing for the page |
| BREPOSITORY_SOURCE         | content/data/repository.yaml | Registry file |
| BREPOSITORY_SET            | set1 | Repository set used, if empty full repository is used.   |
| BREPOSITORY_MODE           | panel | Layout type, panel or list |
| BREPOSITORY_PANEL_COLOR    | panel-info | CSS class used to color the panel template in the default template. Possible values: panel-default, panel-primary, panel-success, panel-info, panel-warning, panel-danger |
| BREPOSITORY_HEADER         | Files | Header text  |

Example:

    Title: Test page
    Date: 2017-01-05 10:20
    Category: test
    Slug: test-page
    Author: Test Person
    brepository: True
    brepository_set: set1
    brepository_header: Files

Repository listing is available in template in variable `page.brepository` or `article.brepository`

### Div wise parameters

Valid for `<div>` classes `brepository` and `brepository-item`:

| Parameter                 | Example value     | Description  |
|---------------------------|-------------------|--------------|
| data-source               | content/data/repository.yaml | Registry file
| data-set                  | set1              | Repository set used, if empty full personnel is used.  |
| data-mode                 | panel             | Layout type, panel or list |
| data-header               | Files             | Header text |
| data-panel-color          | panel-info | CSS class used to color the panel template in the default template. Possible values: panel-default, panel-primary, panel-success, panel-info, panel-warning, panel-danger |

Valid for `brepository-item`:

| Parameter                 | Example value     | Description  |
|---------------------------|-------------|--------------|
| data-item                 | Item1             | Item name shown  |

Example listing:

    <div class="brepository" data-source="content/data/repository.yaml" data-set="set1"></div>

Example of repository item:   

    Title: Test page
    Date: 2017-01-05 10:20
    Category: test
    Slug: test-page
    Author: Test Person
    brepository_header: People    
    brepository_source: content/data/repository.yaml
    <div class="brepository-item" data-item="file1"></div>
