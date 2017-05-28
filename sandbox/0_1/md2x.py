# LOGGING FUNCTION BEFORE LOGGING MODULE SETUP
def print_logging(message):
    print('PRINT : ' + message)

import logging
import argparse
import configparser

import os
import os.path as path
import shutil
import re
import markdown as markdown_mod
import bs4
import pdfkit

###################
### Version 0.1 ###
###################

CONFIG_TEMPLATE_V0_1 = '''[basic]
version : 0.1

[logging]
level : DEBUG
write_to_file : False
file : log.out

[directory]
markdown : markdown
html : html
template : template

[template]
template : TEMPLATE.template
replace : REPLACE.replace

[01.md]
html : index.html

[02.md]
html : 02.html
template : 02.template
replace : 02.replace
'''

class Md2Html_v0_1:

    def __init__(self, config_path):
        self.config_path = config_path

        # basic
        self.bootstrap = False

        # directory
        self.dir_markdown = None
        self.dir_output = None
        self.dir_template = None
        self.dir_pdf = None

        # template and markdown
        self.conv_template = None
        self.conv_replace = None
        self.conv_markdown_dict = {}

        # pdf
        self.pdf_output = None
        self.pdf_css = []
        self.pdf_dpi = None
        self.pdf_markdowns = []

        # VAL
        self.VERSION = '0.1'
        self.TYPE_HTML = 'html'
        self.TYPE_PDF = 'pdf'

    def run(self):
        self.cd_to_script_dir()

        #  LOAD CONFIG
        config_text = self.get_config_text(self.config_path)
        config = self.get_config(config_text)
        output_type = self.load_basic_section(config)
        output_type = output_type.lower()
        if output_type == 'html':
            output_type = self.TYPE_HTML
        elif output_type == 'pdf':
            output_type = self.TYPE_PDF
        else:
            print_logging('Critical : option output_type at section [basic] must be "html" or "pdf"')
            print_logging('abort')
            exit(1)

        self.load_logging_section(config)
        self.load_directory_section(config, output_type)
        self.load_template_section(config)
        self.load_markdown_sections(config, output_type)
        if(output_type == self.TYPE_PDF):
            self.load_pdf_section(config)

        # CHECK FILES
        self.check_directory_exist(output_type)
        self.check_template_exist()
        self.check_markdown_exist(output_type)
        if(output_type == self.TYPE_PDF):
            self.check_pdf_exist()


        # CONVERT
        if(output_type == self.TYPE_HTML):
            self.convert_html()
            self.copy_other_files()
        elif(output_type == self.TYPE_PDF):
            #self.convert_pdf()
            pass


    def cd_to_script_dir(self):
        print_logging('cd to script dir : start')
        try:
            absfilepath = os.path.abspath(__file__)
            absdirpath = path.dirname(absfilepath)
            print_logging('    directory : "{}"'.format(absdirpath))
            os.chdir(absdirpath)
        except Exception as e:
            print_logging('    {}'.format(e))
            print_logging('cd to script dir : fail')
            print_logging('abort')
            exit(1)

        print_logging('cd to script dir : success')


    ###################
    ### CONFIG LOAD ###
    ###################

    def get_config_text(self, config_path):
        print_logging('get config text : start')
        try:
            if not path.exists(config_path):
                print_logging('config file doesn\'t exit. "{}"'.format(config_path))
                print_logging('create sample file and abort')
                with open(config_path, 'w') as fout:
                    fout.write(CONFIG_TEMPLATE_V0_1)
                exit(1)

            print_logging('config file exist. "{}"'.format(config_path))

            with open(config_path, 'r') as fin:
                config_text = fin.read()

        except Exception as e:
            print_logging(e)
            print_logging('get config text : fail')
            print_logging('abort')
            exit(1)

        print_logging('get config text : success')
        return config_text

    def get_config(self, config_text):
        print_logging('get config-object from text : start')
        try:
            config = configparser.ConfigParser()
            config.read_string(config_text)

        except Exception as e:
            print_logging('    {}'.format(e))
            print_logging('get config-object from text : fail')
            print_logging('abort')
            exit(1)

        print_logging('get config-object from text : success')
        return config


    def load_basic_section(self, config):
        print_logging('load config [basic] section : start')
        try:
            version = config.get('basic', 'version')
            output_type = config.get('basic', 'output_type')
            print_logging('loading [basic] section success')

            if config.has_option('basic', 'bootstrap'):
                bootstrap = config.get('basic', 'bootstrap').upper()
                if bootstrap == 'TRUE':
                    self.bootstrap = True
                elif wtf == 'FALSE':
                    self.bootstrap = False
                else:
                    print_logging('   option bootstrap at section [basic] must be "True" or "False"')
                    raise

            if version != self.VERSION:
                print_logging('    found version mismatch')
                print_logging('    args {}'.format(self.VERSION))
                print_logging('    config file {}'.format(version))
                raise

        except Exception as e:
            print_logging('    {}'.format(e))
            print_logging('load config [basic] section : fail')
            exit(1)

        print_logging('load config [basic] section : success')
        return output_type


    def load_logging_section(self, config):
        print_logging('load config [logging] section : start')
        write_to_file = False
        log_file = ''

        try:
            level_str = config.get('logging', 'level').upper()
            level_upper = level_str.upper()
            if level_upper == 'CRITICAL':
                level = logging.CRITICAL
            elif level_upper == 'ERROR':
                level = logging.ERROR
            elif level_upper == 'WARNING':
                level = logging.WARNING
            elif level_upper == 'INFO':
                level = logging.INFO
            elif level_upper == 'DEBUG':
                level = logging.DEBUG
            else:
                print_logging('    option level "{}" is not supported'.format(level_str))
                print_logging('    print chose one of them [CRITICAL, ERROR, WARNING, INFO, DEBUG]')
                raise

            if config.has_option('logging', 'write_to_file'):
                wtf = config.get('logging', 'write_to_file').upper()
                if wtf == 'TRUE':
                    write_to_file = True
                    log_file = config.get('logging', 'file')
                elif wtf == 'FALSE':
                    write_to_file = False
                else:
                    print_logging('   option write_to_file must be "True" or "False"')
                    raise

            if write_to_file:
                logfmt = '%(asctime)s %(levelname)s : %(message)s'
                datefmt='%Y-%m-%d %H:%M:%S'
                logging.basicConfig(level=level, format=logfmt, datefmt=datefmt)

            else:
                logfmt = '%(asctime)s %(levelname)s : %(message)s'
                datefmt='%Y-%m-%d %H:%M:%S'
                logging.basicConfig(level=level, format=logfmt, datefmt=datefmt)

        except Exception as e:
            print_logging('    {}'.format(e))
            print_logging('load config [logging] section : fail')
            print_logging('abort')
            exit(1)

        logging.debug('    level = "{}"'.format(level_upper))
        logging.debug('    write_to_file = "{}"'.format(write_to_file))
        logging.debug('    file = "{}"'.format(log_file))
        logging.info('load config [logging] section : success')


    def load_directory_section(self, config, output_type):
        logging.info('load config [directory] section : start')

        try:
            dir_markdown = config.get('directory', 'markdown')
            self.dir_markdown = os.path.abspath(dir_markdown)

            dir_output = config.get('directory', 'output')
            self.dir_output = os.path.abspath(dir_output)

            dir_template = config.get('directory', 'template')
            self.dir_template = os.path.abspath(dir_template)

            if config.has_option('directory', 'pdf'):
                dir_pdf = config.get('directory', 'pdf')
                self.dir_pdf = os.path.abspath(dir_pdf)
            else:
                if output_type == self.TYPE_PDF:
                    logging.warning('output_type pdf requires pdf option at section directory')
                    raise

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('load config [directory] section : fail')
            logging.critical('abort')
            exit(1)

        logging.debug('    markdown : "{}"'.format(self.dir_markdown))
        logging.debug('    output : "{}"'.format(self.dir_output))
        logging.debug('    template : "{}"'.format(self.dir_template))
        logging.debug('    pdf : "{}"'.format(self.dir_pdf))
        logging.info('load config [directory] section : success')

    def load_template_section(self, config):
        logging.info('load config [template] section : start')
        try:
            abs_template = config.get('template', 'template')
            if not path.isabs(abs_template):
                abs_template = path.join(self.dir_template, abs_template)
            self.conv_template = abs_template

            abs_replace = config.get('template', 'replace')
            if not path.isabs(abs_replace):
                abs_replace = path.join(self.dir_template, abs_replace)
            self.conv_replace = abs_replace

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('load config [template] section : fail')
            logging.critical('abort')
            exit(1)

        logging.debug('    template : "{}"'.format(self.conv_template))
        logging.debug('    replace : "{}"'.format(self.conv_replace))
        logging.info('load config [template] section : success')


    def load_markdown_sections(self, config, output_type):
        logging.info('load config markdown sections : start')
        try:
            dict_markdown = {}
            markdown_sections = filter(lambda text : text.endswith('.md'), config.sections())
            for markdown_section in markdown_sections:
                logging.info('    section [{}] : start'.format(markdown_section))
                d = {}

                # markdown path
                markdown_path = path.join(self.dir_markdown, markdown_section)
                d['markdown'] = markdown_path

                # html path
                if config.has_option(markdown_section, 'html'):
                    html_path = config.get(markdown_section, 'html')
                    if not path.isabs(html_path):
                        html_path = path.join(self.dir_output, html_path)
                    d['html'] = html_path
                else:
                    if output_type == self.TYPE_HTML:
                        logging.warning('    output_type "html" needs html option at markdown section')
                        raise

                # specific template path
                if config.has_option(markdown_section, 'template'):
                    template = config.get(markdown_section, 'template')
                    if not path.isabs(template):
                        template = path.join(self.dir_template, template)
                    d['template'] = template

                # specific replace path
                if config.has_option(markdown_section, 'replace'):
                    replace = config.get(markdown_section, 'replace')
                    if not path.isabs(replace):
                        replace = path.join(self.dir_template, replace)
                    d['replace'] = replace

                dict_markdown[markdown_section] = d

                for (key, value) in d.items():
                    logging.debug('        {} : {}'.format(key, value))
                logging.info('    section [{}] : success'.format(markdown_section))


            self.conv_markdown_dict = dict_markdown

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('load config markdown sections : fail')
            logging.critical('abort')
            exit(1)

        logging.info('load config markdown sections : success')


    def load_pdf_section(self, config):
        logging.info('load [pdf] section : start')
        try:
            output = config.get('pdf', 'output')
            if not path.isabs(output):
                output = path.join(self.dir_output, output)
            self.pdf_output = output

            css_str = config.get('pdf', 'css')
            css_files = []
            for css in css_str.split(','):
                css = css.strip()
                css = path.join(self.dir_pdf, css)
                css_files.append(css)
            self.pdf_css = css_files

            dpi = config.get('pdf', 'dpi')
            self.pdf_dpi = int(dpi)

            markdowns_str = config.get('pdf', 'markdowns')
            markdowns = []
            for markdown in markdowns_str.split(','):
                markdown = markdown.strip()
                markdown_path = path.join(self.dir_markdown, markdown)
                markdowns.append((markdown, markdown_path))
            self.pdf_markdowns = markdowns

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('load [pdf] section : fail')
            logging.critical('abort')
            exit(1)

        logging.debug('    output : {}'.format(self.pdf_output))
        logging.debug('    css : {}'.format(self.pdf_css))
        logging.debug('    dpi : {}'.format(self.pdf_dpi))
        logging.debug('    markdowns : [')
        for markdown in self.pdf_markdowns:
            logging.debug('        {},'.format(markdown))
        logging.debug('    ]')
        logging.info('load [pdf] section : success')


    ########################
    ### CHECK FILE EXIST ###
    ########################

    def check_directory_exist(self, output_type):
        logging.info('check all directory exist : start')
        try:
            # Markdown Directory
            dir_markdown = self.dir_markdown
            if not path.isdir(dir_markdown):
                logging.warning('    markdown : not exist')
                logging.warning('    {}'.format(dir_markdown))
                raise
            logging.info('    markdown : exist')

            # HTML Directory
            dir_output = self.dir_output
            if not path.isdir(dir_output):
                if not path.isfile(dir_output):
                    logging.info('    output : not exist. create')
                    logging.info('    {}'.format(dir_output))
                    os.mkdir(dir_output)
                else:
                    logging.warning('    output : directory not exist. but file exist.')
                    logging.warning('    {}'.format(dir_output))
                    raise
            else:
                logging.info('    output : exist'.format())

            # Template Directory
            dir_template = self.dir_template
            if not path.isdir(dir_template):
                logging.warning('    template : not exist')
                logging.warning('    {}'.format(dir_template))
                raise
            logging.info('    template : exist')

            # PDF Directory
            if(output_type == self.TYPE_PDF):
                dir_pdf = self.dir_pdf
                if not path.isdir(dir_pdf):
                    logging.warning('    pdf : not exist')
                    logging.warning('    {}'.format(dir_pdf))
                    raise
                logging.info('    pdf : exist')

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('check all directory exist : fail')
            logging.critical('abort')
            exit(1)

        logging.info('check all directory exist : success')

    def check_template_exist(self):
        logging.info('check basic template exist : start')
        try:
            template = self.conv_template
            if not path.isfile(template):
                logging.warning('   template : not exit')
                logging.warning('   {}'.format(template))
                raise
            logging.info('    template : exist')

            replace = self.conv_replace
            if not path.isfile(replace):
                logging.warning('   replace : not exit')
                logging.warning('   {}'.format(replace))
                raise
            logging.info('    replace : exist')

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('check basic template exist : fail')
            logging.critical('abort')
            exit(1)

        logging.info('check basic template exist : success')

    def check_markdown_exist(self, output_type):
        logging.info('check markdown files exist : start')
        try:
            for (name, mapping) in self.conv_markdown_dict.items():
                logging.info('    check markdown "{}"'.format(name))
                for (key, value) in mapping.items():
                    if key == 'html':
                        continue
                    if not path.isfile(value):
                        logging.warning('        {} : not exist.'.format(key))
                        logging.warning('        {}'.format(value))
                        raise
                    logging.info('        {} : exist.'.format(key))

            if(output_type == self.TYPE_PDF):
                logging.info('    check pdf markdowns')
                for (md_name, md_path) in self.pdf_markdowns:
                    if not path.isfile(md_path):
                        logging.warning('        {} : not exist.'.format(md_name))
                        logging.warning('        {}'.format(md_path))
                        raise
                    logging.info('        {} : exist'.format(md_name))

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('check markdown files exist : fail')
            logging.critical('abort')
            exit(1)

        logging.info('check markdown files exist : success')

    def check_pdf_exist(self):
        logging.info('check pdf files exist : start')
        try:
            logging.info('    check css files')
            for css in self.pdf_css:
                if not path.isfile(css):
                    logging.warning('        {} : not exist.'.format(css))
                    raise
                logging.info('        {} : exist'.format(css))

        except Exception as e:
            logging.critical('    {}'.format(e))
            logging.critical('check pdf files exist : fail')
            logging.critical('abort')
            exit(1)

        logging.info('check pdf files exist : success')


    ###############
    ### CONVERT ###
    ###############

    def convert_html(self):
        logging.info('convert html : start')
        try:
            for (markdown, d) in self.conv_markdown_dict.items():
                logging.info('    markdown : {}'.format(markdown))

                path_markdown = d['markdown']
                path_html = d['html']
                path_template = self.conv_template
                if 'template' in d:
                    path_template = d['template']
                path_replaces = [self.conv_replace]
                if 'replace' in d:
                    path_replaces.insert(0, d['replace'])
                logging.debug(('        load path info : success'))

                # markdown html
                text_markdown = self.read_file(path_markdown)
                html_markdown = self.convert_markdown_to_html(text_markdown)
                if self.bootstrap:
                    html_markdown = self.modify_html_bootstrap(html_markdown)
                logging.debug(('        convert markdown to content html : success'))

                # include markdown html to template html
                html_template = self.get_template_html(path_template)
                html = self.modify_html_include_markdown_html(html_markdown, html_template)
                logging.debug(('        include content html to template html : success'))

                # replace keywords
                for replace in path_replaces:
                    html = self.modify_html_keyword(html, replace)
                all_changed = self.check_all_keywords_changed(html)
                if not all_changed:
                    raise
                logging.debug(('        replayce keywords : success'))


                # write
                with open(path_html, 'w') as fout:
                    fout.write(html)
                logging.debug(('        write to file : success'))

        except Exception as e:
            logging.critical('   {}'.format(e))
            logging.info('convert html : fail')
            exit(1)

        logging.info('convert html : success')


    def convert_pdf(self):
        try:
            for (markdown, path_markdown) in self.pdf_markdowns:
                template = self.conv_template
                path_replaces = [self.conv_replace]
                if markdown in self.conv_markdown_dict:
                    d = self.conv_markdown_dict[markdown]
                    if 'template' in d:
                        path_template = d['template']
                    if 'replace' in d:
                        path_replaces.insert(0, d['replace'])

                # markdown html
                text_markdown = self.read_file(path_markdown)
                html_markdown = self.convert_markdown_to_html(text_markdown)
                if self.bootstrap:
                    html_markdown = self.modify_html_bootstrap(html_markdown)

                # include
                html_template = self.get_template_html(path_template)
                html = modify_html_include_markdown_html(html_markdown, html_template)

                # replace
                for replace in path_replaces:
                    html = modify_html_keyword(html, replace)
                all_changed = check_all_keywords_changed(html)
                if not all_changed:
                    raise

                # change URL to local
                basedir = ''
                html = self.modify_html_url_localize(html, basedir)

                # change html to pdf
                binary = convert_html_to_pdf(self, html)

        except Exception as e:
            exit(1)


    def copy_other_files(self):
        try:
            dir_markdown = self.dir_markdown
            dir_output = self.dir_output
            files = os.listdir(dir_markdown)

            def is_copy_target(file_name):
                if file_name.endswith('.md'):
                    return False
                if file_name in ['.DS_Store']:
                    return False
                return True

            files = filter(is_copy_target, files)
            for file_name in files:
                src_path = path.join(dir_markdown, file_name)
                dst_path = path.join(dir_output, file_name)

                if path.isfile(src_path):
                    shutil.copyfile(src_path, dst_path)
                elif path.isdir(src_path):
                    if path.isfile(dst_path):
                        os.remove(dst_path)
                    elif path.isdir(dst_path):
                        shutil.rmtree(dst_path)
                    shutil.copytree(src_path, dst_path)
                else:
                    raise

                print(src_path, dst_path)
        except Exception as e:
            logging.warning(e)
            logging.critical('Copy files fail')
            exit(1)


    ######################
    ### CONVERT HELPER ###
    ######################

    def read_file(self, file_path):
        if not hasattr(self, '_file_cache'):
            self._file_cache = {}

        if file_path not in self._file_cache:
            with open(file_path, 'r') as fin:
                self._file_cache[file_path] = fin.read()

        return self._file_cache[file_path]


    def convert_markdown_to_html(self, markdown_text):
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite'
        ]

        html = markdown_mod.markdown(markdown_text, extensions=extensions)
        return html


    def modify_html_bootstrap(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')

        # IMAGE
        tags = soup.find_all('img')
        for tag in tags:
            if tag.has_attr('class'):
                attr_list = tag['class']
                if 'img-responsive' not in attr_list:
                    attr_list.append('img-responsive')
                    tag['class'] = attr_list
            else:
                tag['class'] = 'img-responsive'

        return soup.prettify(soup.original_encoding)


    def get_template_html(self, path_template):
        html = self.read_file(path_template)
        if '{{ MARKDOWN }}' not in html:
            logging.warning('template "{}" doesn\'t have {{ MARKDOWN }}'.format(path_template))
            raise

        return html


    def modify_html_include_markdown_html(self, markdown_html, template_html):
        html = template_html.replace('{{ MARKDOWN }}', markdown_html)
        return html


    def modify_html_keyword(self, html, replace_path):

        r = re.compile(r'{{\s+(\w+)\s+}}')
        def replace_line(line, replace_dict):
            m = r.search(line)
            if m:
                keyword = m.group(1)
                if keyword in replace_dict:
                    line = line.replace(m.group(0), replace_dict[keyword])
            return line

        # Load replace pattern
        replace_text = self.read_file(replace_path)
        replace_dict = {}
        exec(replace_text, locals(), replace_dict)

        # Replace line
        new_lines = []
        for line in html.split('\n'):
            new_lines.append(replace_line(line, replace_dict))

        # make new html
        html = '\n'.join(new_lines)
        return html


    def check_all_keywords_changed(self, html_text):
        try:
            r = re.compile(r'{{\s+(\w+)\s+}}')
            for line in html_text.split('\n'):
                m = r.search(line)
                if m:
                    logging.warning('find unreplaced keyword at "{}"'.format(line))
                    return False
            return True

        except Exception as e:
            exit(1)

    def convert_html_to_pdf(self, html):

        return 'pdf'

    def modify_html_url_localize(self, html, basedir):

        return html


    def __convert_from_markdown_to_html(self):

        try:
            markdowns = filter(lambda text : text.endswith('.md'), self.dict_markdown.keys())
            for markdown in markdowns:
                logging.info('start converting {}.'.format(markdown))
                dict_md = self.dict_markdown[markdown]

                # CONVERT
                path_md = dict_md['markdown']
                text_md = get_file_content(path_md)
                content_html = markdown_mod.markdown(text_md, extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite'])

                #content_html = md.convert(text_md)
                content_html = add_bootstrap_class(content_html)
                content_html = '\n<!-- GENERATED HTML START -->\n {} \n<!-- GENERATED HTML END -->\n'.format(content_html)
                logging.debug('    convert done')

                # TEMPLATE
                path_template = dict_md.get('template', self.dict_markdown['template'])
                template_text = get_file_content(path_template)
                if '{{ MARKDOWN }}' not in template_text:
                    logging.warning('template "{}" doesn\'t have {{ MARKDOWN }}'.format(path_template))
                    raise
                logging.debug('   load template done')

                # INCLUDE
                html = template_text.replace('{{ MARKDOWN }}', content_html)
                logging.debug('   include done')

                # REPLACE
                if 'replace' in dict_md:
                    path_replace = dict_md['replace']
                    html = replace_keywords(html, path_replace)

                path_replace = self.dict_markdown['replace']
                html = replace_keywords(html, path_replace)

                if not all_keywords_changed(html):
                    logging.warning('template "{}" for markdown "{}"'.format(path_template, path_md))
                    raise
                logging.debug('   replace done')

                path_html = dict_md['html']
                with open(path_html, 'w') as fout:
                    fout.write(html)

                logging.info('convert markdown [{}] done'.format(markdown))
            logging.info('all markdown convert done')

        except Exception as e:
            logging.critical('Failed converting from markdown to html. {}'.format(e))
            exit(1)


    def __check_html(self):
        pass


###########
### RUN ###
###########

def run():
    Md2Html_v0_1('html.conf').run()
    print('\n\n\n')
    Md2Html_v0_1('print.conf').run()
    #print('\n\n\n')
    #Md2Html_v0_1('pdf.conf').run()

def test():
    pass

if __name__ == '__main__':
    run()