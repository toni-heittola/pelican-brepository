# -*- coding: utf-8 -*-
"""
File repository -- BREPOSITORY
========================
Author: Toni Heittola (toni.heittola@gmail.com)

"""

import os
import shutil
import logging
import copy
from bs4 import BeautifulSoup
from jinja2 import Template
from pelican import signals, contents
import datetime
import yaml
import operator
import re

logger = logging.getLogger(__name__)
__version__ = '0.1.0'

brepository_default_settings = {
    'panel-color': 'panel-info',
    'header': 'Repository',
    'mode': 'panel',
    'template': {
        'panel': """
            <div class="panel {{ panel_color }}">
              {% if header %}
              <div class="panel-heading">
                <h3 class="panel-title">{{header}}</h3>
              </div>
              {% endif %}
              <table class="table brepository-container">
              {{list}}
              </table>
            </div>
        """,
        'list': """
            {% if header %}
                <h3 class="section-heading text-center">{{header}}</h3>
            {% endif %}
            <div class="list-group brepository-container">
                {{list}}
            </div>
        """},
    'item-template': {
        'panel': """
            <tr>
                {% if type_icon %}
                <td class="text-center {{item_css}}">
                    <a class="icon" href="{{url}}">
                    {{type_icon}}
                    </a>
                    {% if size %}<span class="clearfix small text-muted">{{size}}</span>{% endif %}
                </td>
                {% endif %}
                <td class="{{item_css}}">
                    <div class="row">
                        <div class="col-md-12">
                        {% if url %}
                        <a href="{{url}}" target="_blank">
                        {% endif %}
                        {% if title %}
                            <h5>{{title}}</h5>
                        {% endif %}
                        {% if url %}
                        </a>
                        {% endif %}
                        </div>
                        <div class="col-md-12">
                            {% if version or package_type%}
                            <span class="text-muted">
                                {% if version %}
                                version {{version}}
                                {% endif %}
                                {% if package_type %}
                                (.{{package_type}})
                                {% endif %}
                            </span>
                            {% endif %}
                            {% if password%}
                            <br>
                            <strong>
                            password "{{password}}"
                            </strong>
                            {% endif %}
                        </div>
                    </div>
                </td>
            </tr>
        """,
        'list': """
            <a class="list-group-item {{item_color}}" href="{{url}}" target="_blank">
            <div class="row">
                {% if type_icon %}
                <div class="col-md-1 col-sm-2">
                    {{type_icon}}
                </div>
                {% endif %}
                <div class="col-md-11 col-sm-10">
                    {% if title %}
                        <h4 class="list-group-item-heading {{item_css}}">{{title}} <i class="fa fa-download"></i></h4>
                    {% endif %}
                    {% if size %}
                        <span class="text-muted">({{size}})</span>
                        <br>
                    {% endif %}
                    {% if version or package_type or password %}
                        <span class="text-muted">
                        {% if version %}
                            version {{version}}
                        {% endif %}
                        {% if package_type %}
                            (.{{package_type}})
                        {% endif %}
                        </span>
                    {% endif %}
                    {% if password %}
                        <br>
                        <strong>
                        password "{{password}}"
                        </strong>
                    {% endif %}
                </div>
            </div>
            </a>
        """},
    'item-card': """
        <div class="row">
            {% if type_icon %}
            <div class="col-md-1">
                <a class="icon" href="{{url}}" target="_blank">
                {{type_icon}}
                </a>
            </div>
            {% endif %}
            <div class="col-md-11">
                {% if url %}
                <a href="{{url}}" target="_blank">
                {% endif %}
                {% if title %}
                    <span style="font-size:20px;">{{title}} <i class="fa fa-download"></i></span>
                {% endif %}
                {% if url %}
                </a>
                {% endif %}
                {% if size %}
                <span class="text-muted">({{size}})</span>
                {% endif %}
                <br>
                {% if DOI %}<a href="{{DOI}}">{% endif %}
                {% if DOI_img %}{{DOI_img}}{% endif %}
                {% if DOI %}</a>{% endif %}
                {% if version or package_type or password%}
                <span class="text-muted">
                {% if version %}
                version {{version}}
                {% endif %}
                {% if package_type %}
                (.{{package_type}})
                {% endif %}
                </span>
                {% endif %}
                {% if password%}
                <br>
                <strong>
                password "{{password}}"
                </strong>
                {% endif %}
            </div>
        </div>
    """,
    'type-icons': {
      'audio': """
          <span class="fa-stack fa-2x">
            <i class="fa fa-square fa-stack-2x text-success"></i>
            <i class="fa fa-file-audio-o fa-stack-1x fa-inverse"></i>
          </span>
      """,
      'git': """
        <span class="fa-stack fa-2x">
            <i class="fa fa-square fa-stack-2x "></i>
            <i class="fa fa-github fa-stack-1x fa-inverse"></i>
        </span>
      """,
      'python': """
        <span class="fa-stack fa-2x">
            <i class="fa fa-square fa-stack-2x text-success"></i>
            <i class="fa icon-python fa-stack-1x fa-inverse"></i>
        </span>
      """,
      'jquery': """
        <span class="fa-stack fa-2x">
            <i class="fa fa-square fa-stack-2x text-info"></i>
            <i class="fa icon-jquery fa-stack-1x fa-inverse"></i>
        </span>
      """,
      'php': """
        <span class="fa-stack fa-2x">
            <i class="fa fa-square fa-stack-2x text-warning"></i>
            <i class="fa icon-php fa-stack-1x fa-inverse"></i>
        </span>
      """,
      'javascript': """
        <span class="fa-stack fa-2x">
            <i class="fa fa-square fa-stack-2x text-info"></i>
            <i class="fa icon-javascript fa-stack-1x fa-inverse"></i>
        </span>
      """,
      'c': """
        <span class="fa-stack fa-2x">
            <i class="fa fa-square fa-stack-2x text-danger"></i>
            <i class="fa icon-c fa-stack-1x fa-inverse"></i>
        </span>
      """,
      'cplusplus': """
        <span class="fa-stack fa-2x">
            <i class="fa fa-square fa-stack-2x text-danger"></i>
            <i class="fa icon-cplusplus fa-stack-1x fa-inverse"></i>
        </span>
      """,
      'html5': """
        <span class="fa-stack fa-2x">
            <i class="fa fa-square fa-stack-2x text-warning"></i>
            <i class="fa icon-html5 fa-stack-1x fa-inverse"></i>
        </span>
      """,

      'python-package': """
        <span class="fa-stack fa-2x">
          <i class="fa fa-square fa-stack-2x text-warning"></i>
          <i class="fa fa-gears fa-stack-1x fa-inverse"></i>
        </span>
      """,

      'matlab-package': """
        <span class="fa-stack fa-2x">
            <i class="fa fa-square fa-stack-2x text-info"></i>
            <i class="fa fa-gears fa-stack-1x fa-inverse"></i>
        </span>
      """,
      'latex': """
        <span class="fa-stack fa-2x">
            <i class="fa fa-square fa-stack-2x text-muted"></i>
            <i class="fa fa-file-text-o fa-stack-1x fa-inverse"></i>
        </span>
      """,
      'word': """
        <span class="fa-stack fa-2x">
          <i class="fa fa-square fa-stack-2x text-muted"></i>
          <i class="fa fa-file-word-o fa-stack-1x fa-inverse"></i>
        </span>
      """,
      'doc': """
        <span class="fa-stack fa-2x">
          <i class="fa fa-square fa-stack-2x text-muted"></i>
          <i class="fa fa-file-text-o fa-stack-1x fa-inverse"></i>
        </span>
      """,
      'theme': """
        <span class="fa-stack fa-2x">
          <i class="fa fa-square fa-stack-2x text-warning"></i>
          <i class="fa fa-file-image-o fa-stack-1x fa-inverse"></i>
        </span>
      """
    },
    'data-source': None,
    'set': None,
    'show': False,
    'minified': True,
    'generate_minified': True,
    'template-variable': False,
    'item': None,
    'site-url': '',
    'debug_processing': False
}

brepository_settings = copy.deepcopy(brepository_default_settings)


def search(name, repository):
    return [element for element in repository if element['name'] == name]


def load_repository(source):
    """

    :param source: filename of the data file
    :return: registry
    """

    if source and os.path.isfile(source):
        try:
            from distutils.version import LooseVersion
            if LooseVersion(str(yaml.__version__)) >= "5.1":
                with open(source, 'r') as field:
                    repository = yaml.load(field, Loader=yaml.FullLoader)
            else:
                with open(source, 'r') as field:
                    repository = yaml.load(field)

            if 'sets' in repository and 'repository' in repository:
                set_data = {}
                for set in repository['sets']:
                    item_list = []
                    for item_name in repository['sets'][set]:
                        tmp = search(name=item_name, repository=repository['repository'])
                        if tmp:
                            item_list.append(tmp[0])
                    set_data[set] = item_list
                repository['sets'] = set_data

            return repository

        except ValueError:
            logger.warn('`pelican-brepository` failed to load file [' + str(source) + ']')
            return False

    else:
        logger.warn('`pelican-brepository` failed to load file [' + str(source) + ']')
        return False


def get_attribute(attrs, name, default=None):
    """
    Get div attribute
    :param attrs: attribute dict
    :param name: name field
    :param default: default value
    :return: value
    """

    if 'data-'+name in attrs:
        return attrs['data-'+name]
    else:
        return default


def generate_listing_item(item_data, settings):
    """
    Generate repository listing item

    :param item_data: item data dict
    :param settings: settings dict
    :return: html content
    """

    if 'type' in item_data and item_data['type'] in settings['type-icons']:
        type_icon = settings['type-icons'][item_data['type']]
    else:
        type_icon = None

    template = Template(settings['item-template'][settings['mode']].strip('\t\r\n').replace('&gt;', '>').replace('&lt;', '<'))
    html = BeautifulSoup(template.render(site_url=settings['site-url'],
                                         type_icon=type_icon,
                                         title=item_data['title'] if 'title' in item_data else '',
                                         url=item_data['url'] if 'url' in item_data else '',
                                         type=item_data['type'] if 'type' in item_data else '',
                                         size=item_data['size'] if 'size' in item_data else '',
                                         DOI=item_data['DOI'] if 'DOI' in item_data else '',
                                         DOI_img=item_data['DOI_img'] if 'DOI_img' in item_data else '',
                                         version=item_data['version'] if 'version' in item_data else '',
                                         password=item_data['password'] if 'password' in item_data else '',
                                         package_type=item_data['package-type'] if 'package-type' in item_data else '',
                                         ), "html.parser")
    return html.decode()


def generate_item_card(settings):
    """
    Generate item information card

    :param settings: settings dict
    :return: bs4 element
    """

    repository = load_repository(source=settings['data-source'])
    item_data = search(name=settings['item'], repository=repository['repository'])
    if item_data:
        item_data = item_data[0]
    else:
        logger.warn('`pelican-brepository` failed to load item [' + str(settings['item']) + ']')
        return False

    if 'type' in item_data and item_data['type'] in settings['type-icons']:
        type_icon = settings['type-icons'][item_data['type']]
    else:
        type_icon = None
    template = Template(settings['item-card'].strip('\t\r\n').replace('&gt;', '>').replace('&lt;', '<'))

    html = BeautifulSoup(template.render(site_url=settings['site-url'],
                                         type_icon= type_icon,
                                         title=item_data['title'] if 'title' in item_data else '',
                                         url=item_data['url'] if 'url' in item_data else '',
                                         type=item_data['type'] if 'type' in item_data else '',
                                         size=item_data['size'] if 'size' in item_data else '',
                                         DOI=item_data['DOI'] if 'DOI' in item_data else '',
                                         DOI_img=item_data['DOI_img'] if 'DOI_img' in item_data else '',
                                         version=item_data['version'] if 'version' in item_data else '',
                                         password=item_data['password'] if 'password' in item_data else '',
                                         package_type=item_data['package-type'] if 'package-type' in item_data else '',
                                         ), "html.parser")

    return html


def generate_listing(settings):
    """
    Generate repository listing

    :param settings: settings dict
    :return: bs4 element
    """
    repository = load_repository(source=settings['data-source'])
    if settings['set'] and 'sets' in repository and settings['set'] in repository['sets']:
        repository = repository['sets'][settings['set']]
    else:
        repository = repository['repository']

    if repository:
        html = "\n"
        for item_data in repository:
            html += generate_listing_item(item_data=item_data, settings=settings) + "\n"
        html += "\n"

        template = Template(settings['template'][settings['mode']].strip('\t\r\n').replace('&gt;', '>').replace('&lt;', '<'))

        return BeautifulSoup(template.render(list=html,
                                             header=settings['header'],
                                             site_url=settings['site-url'],
                                             panel_color=settings['panel-color'], ), "html.parser")


def brepository(content):
    """
    Main processing

    """

    if isinstance(content, contents.Static):
        return

    soup = BeautifulSoup(content._content, 'html.parser')
    # Template variable
    if brepository_settings['template-variable']:
        # We have page variable set
        brepository_settings['show'] = True
        div_html = generate_listing(settings=brepository_settings)
        if div_html:
            content.brepository = div_html.decode()

    else:
        content.brepository = None

    brepository_divs = soup.find_all('div', class_='brepository')
    brepository_item_divs = soup.find_all('div', class_='brepository-item')

    if brepository_divs:
        if brepository_settings['debug_processing']:
            logger.debug(msg='[{plugin_name}] title:[{title}] divs:[{div_count}]'.format(
                plugin_name='brepository',
                title=content.title,
                div_count=len(brepository_divs)
            ))

        for brepository_div in brepository_divs:

            # We have div in the page
            brepository_settings['show'] = True
            settings = copy.deepcopy(brepository_settings)
            settings['data-source'] = get_attribute(brepository_div.attrs, 'source', brepository_settings['data-source'])
            settings['set'] = get_attribute(brepository_div.attrs, 'set', brepository_settings['set'])
            settings['mode'] = get_attribute(brepository_div.attrs, 'mode', brepository_settings['mode'])
            settings['header'] = get_attribute(brepository_div.attrs, 'header', brepository_settings['header'])
            settings['panel-color'] = get_attribute(brepository_div.attrs, 'panel-color', brepository_settings['panel-color'])

            div_html = generate_listing(settings=settings)
            brepository_div.replaceWith(div_html)

    if brepository_item_divs:
        if brepository_settings['debug_processing']:
            logger.debug(msg='[{plugin_name}] title:[{title}] divs:[{div_count}]'.format(
                plugin_name='brepository-item',
                title=content.title,
                div_count=len(brepository_item_divs)
            ))

        for brepository_item_div in brepository_item_divs:
            # We have div in the page
            brepository_settings['show'] = True
            settings = copy.deepcopy(brepository_settings)
            settings['data-source'] = get_attribute(brepository_item_div.attrs, 'source', brepository_settings['data-source'])
            settings['set'] = get_attribute(brepository_item_div.attrs, 'set', brepository_settings['set'])
            settings['mode'] = get_attribute(brepository_item_div.attrs, 'mode', brepository_settings['mode'])
            settings['header'] = get_attribute(brepository_item_div.attrs, 'header', brepository_settings['header'])
            settings['panel-color'] = get_attribute(brepository_item_div.attrs, 'panel-color', brepository_settings['panel-color'])
            settings['item'] = get_attribute(brepository_item_div.attrs, 'item', brepository_settings['item'])
            div_html = generate_item_card(settings=settings)
            if div_html:
                brepository_item_div.replaceWith(div_html)

    if brepository_settings['show']:

        if brepository_settings['minified']:
            html_elements = {
                'css_include': ['<link rel="stylesheet" href="' + brepository_settings['site-url'] + '/theme/css/font-mfizz.min.css">']
             }
        else:
            html_elements = {
                'css_include': ['<link rel="stylesheet" href="' + brepository_settings['site-url'] + '/theme/css/font-mfizz.css">']
            }

        if u'scripts' not in content.metadata:
            content.metadata[u'scripts'] = []

        if u'styles' not in content.metadata:
            content.metadata[u'styles'] = []
        for element in html_elements['css_include']:
            if element not in content.metadata[u'styles']:
                content.metadata[u'styles'].append(element)

    content._content = soup.decode()


def process_page_metadata(generator, metadata):
    """
    Process page metadata and assign css and styles

    """
    global brepository_default_settings, brepository_settings
    brepository_settings = copy.deepcopy(brepository_default_settings)

    if u'styles' not in metadata:
        metadata[u'styles'] = []
    if u'scripts' not in metadata:
        metadata[u'scripts'] = []

    if u'brepository' in metadata and metadata['brepository'] == 'True':
        brepository_settings['show'] = True
        brepository_settings['template-variable'] = True
    else:
        brepository_settings['show'] = False
        brepository_settings['template-variable'] = False

    if u'brepository_source' in metadata:
        brepository_settings['data-source'] = metadata['brepository_source']

    if u'brepository_set' in metadata:
        brepository_settings['set'] = metadata['brepository_set']

    if u'brepository_mode' in metadata:
        brepository_settings['mode'] = metadata['brepository_mode']

    if u'brepository_panel_color' in metadata:
        brepository_settings['panel-color'] = metadata['brepository_panel_color']

    if u'brepository_header' in metadata:
        brepository_settings['header'] = metadata['brepository_header']


def move_resources(gen):
    """
    Move files from js/css folders to output folder, use minified files.

    """

    plugin_paths = gen.settings['PLUGIN_PATHS']
    if not os.path.exists(os.path.join(gen.output_path, 'theme', 'css')):
        os.makedirs(os.path.join(gen.output_path, 'theme', 'css'))

    if brepository_settings['minified']:
        if brepository_settings['generate_minified']:
            minify_css_directory(gen=gen, source='css', target='css.min')

        css_target = os.path.join(gen.output_path, 'theme', 'css', 'font-mfizz.min.css')
        for path in plugin_paths:
            css_source = os.path.join(path, 'pelican-brepository', 'css.min', 'font-mfizz.min.css')

            if os.path.isfile(css_source):
                shutil.copyfile(css_source, css_target)

            if os.path.isfile(css_target):
                break
    else:
        css_target = os.path.join(gen.output_path, 'theme', 'css', 'font-mfizz.css')
        for path in plugin_paths:
            css_source = os.path.join(path, 'pelican-brepository', 'css', 'font-mfizz.css')

            if os.path.isfile(css_source):
                shutil.copyfile(css_source, css_target)

            if os.path.isfile(css_target):
                break

    # Fonts
    for path in plugin_paths:
        fonts = [
            {'target': os.path.join(gen.output_path, 'theme', 'css', 'font-mfizz.eot'),
             'source': os.path.join(path, 'pelican-brepository', 'font', 'font-mfizz.eot')
             },
            {'target': os.path.join(gen.output_path, 'theme', 'css', 'font-mfizz.svg'),
             'source': os.path.join(path, 'pelican-brepository', 'font', 'font-mfizz.svg')
             },
            {'target': os.path.join(gen.output_path, 'theme', 'css', 'font-mfizz.ttf'),
             'source': os.path.join(path, 'pelican-brepository', 'font', 'font-mfizz.ttf')
             },
            {'target': os.path.join(gen.output_path, 'theme', 'css', 'font-mfizz.woff'),
             'source': os.path.join(path, 'pelican-brepository', 'font', 'font-mfizz.woff')
             },
        ]

        for item in fonts:
            if os.path.isfile(item['source']):
                shutil.copyfile(item['source'], item['target'])
        all_copied = True
        for item in fonts:
            if not os.path.isfile(item['target']):
                all_copied = False
        if all_copied:
            break


def minify_css_directory(gen, source, target):
    """
    Move CSS resources from source directory to target directory and minify. Using rcssmin.

    """
    import rcssmin

    plugin_paths = gen.settings['PLUGIN_PATHS']
    for path in plugin_paths:
        source_ = os.path.join(path, 'pelican-brepository', source)
        target_ = os.path.join(path, 'pelican-brepository', target)
        if os.path.isdir(source_):
            if not os.path.exists(target_):
                os.makedirs(target_)

            for root, dirs, files in os.walk(source_):
                for current_file in files:
                    if current_file.endswith(".css"):
                        current_file_path = os.path.join(root, current_file)
                        with open(current_file_path) as css_file:
                            with open(os.path.join(target_, current_file.replace('.css', '.min.css')), "w") as minified_file:
                                minified_file.write(rcssmin.cssmin(css_file.read(), keep_bang_comments=True))
                    elif current_file.endswith(".eot") or current_file.endswith(".svg") or current_file.endswith(".ttf") or current_file.endswith(".woff"):
                        current_file_path = os.path.join(root, current_file)
                        target_file = os.path.join(target_, current_file)
                        shutil.copyfile(current_file_path, target_file)


def init_default_config(pelican):
    """
    Handle settings from pelicanconf.py

    """
    global brepository_default_settings, brepository_settings

    brepository_default_settings['site-url'] = pelican.settings['SITEURL']

    if 'BREPOSITORY_SOURCE' in pelican.settings:
        brepository_default_settings['data-source'] = pelican.settings['BREPOSITORY_SOURCE']

    if 'BREPOSITORY_TEMPLATE' in pelican.settings:
        brepository_default_settings['template'].update(pelican.settings['BREPOSITORY_TEMPLATE'])

    if 'BREPOSITORY_ITEM_TEMPLATE' in pelican.settings:
        brepository_default_settings['item-template'].update(pelican.settings['BREPOSITORY_ITEM_TEMPLATE'])

    if 'BREPOSITORY_ITEM_CARD_TEMPLATE' in pelican.settings:
        brepository_default_settings['item-card'] = pelican.settings['BREPOSITORY_ITEM_CARD_TEMPLATE']

    if 'BREPOSITORY_PANEL_COLOR' in pelican.settings:
        brepository_default_settings['panel-color'] = pelican.settings['BREPOSITORY_PANEL_COLOR']

    if 'BREPOSITORY_HEADER' in pelican.settings:
        brepository_default_settings['header'] = pelican.settings['BREPOSITORY_HEADER']

    if 'BREPOSITORY_MINIFIED' in pelican.settings:
        brepository_default_settings['minified'] = pelican.settings['BREPOSITORY_MINIFIED']

    if 'BREPOSITORY_GENERATE_MINIFIED' in pelican.settings:
        brepository_default_settings['generate_minified'] = pelican.settings['BREPOSITORY_GENERATE_MINIFIED']

    if 'BREPOSITORY_TYPE_ICONS' in pelican.settings:
        brepository_default_settings['type-icons'].update(pelican.settings['BREPOSITORY_TYPE_ICONS'])

    if 'BREPOSITORY_DEBUG_PROCESSING' in pelican.settings:
        brepository_default_settings['debug_processing'] = pelican.settings['BREPOSITORY_DEBUG_PROCESSING']

    brepository_settings = copy.deepcopy(brepository_default_settings)


def register():
    """
    Register signals

    """

    signals.initialized.connect(init_default_config)
    signals.article_generator_context.connect(process_page_metadata)
    signals.page_generator_context.connect(process_page_metadata)
    signals.article_generator_finalized.connect(move_resources)

    signals.content_object_init.connect(brepository)
