# Introduction

All our public content is built from minimal static webpages made using [Bootstrap CSS](http://getboostrap.com) and [Jekyll](http://jekyllrb.com).

# Getting Started

## Before You Start

You do not have to install Ruby, Rails, or Jekyll to make your own page. The `_config.yml` file contains everything necessary to make a page on-the-fly in minutes. Scroll down to [Configuration](#configuration) for more information.

Of course, should you prefer to test your work locally before committing, keep reading from here.

## Download

* [Download the latest release](https://github.com/softlayer/jumpgate/archive/gh-pages.zip)
* Clone the repo via `git clone -b gh-pages https://github.com/softlayer/jumpgate.git`

## Configuration

The `_config.yml` file contains everything necessary to make a page on-the-fly. Open it using any editor and update the vars (defined below) before push it up to the `gh-pages` branch.

#### Project

* `project` the *public* name for the project
* `lead` high-level description for the product
* `public_url` url for the public GitHub pages

#### GitHub

* `repo` url for this GitHub repository
* `fork` url for forking the repo
* `star` url for stargazers
* `open_issues` url for open, active issues
* `closed_issues` url for closed/archives issues
* `milestones` url for this project's milestones
* `commits` url for this project's commits
* `pulls` url for open pull requests, if any

#### Company

* `www` url for SoftLayer website (do not change)
* `license` url for the MIT license on the repo
* `sldn` url for SoftLayer Development Network (do not change)
* `kb` url for SoftLayer's Knowledgebase (do not change)
* `blog` url for SoftLayer's blog (do not change)

#### Social

* `github` url for all GitHub repositories
* `twitter` url for Twitter account (do not change)

#### Server

* `permalink` defaults to "pretty" (do not change)
* `exclude` a list of files to omit from the _site directory (ex. LICENSE, .gitignore, README.md, CNAME)
* `pygments` defaults to "true" (do not change)
* `safe` defaults to "false" (do not change)

#### Google Analytics

* `ga_tracking_id` SoftLayer's UA ID
* `ga_tracking_domain` SoftLayer's domain for GitHub Pages

## Directory

This is the basic layout of our `gh-pages` directory (not including content specifically written for this project).

<pre>
├── _includes
│   ├── footer.html
│   ├── header.html
│   └── main.html
├── _layout
│   ├── landing.html
│   └── pages.html
├── css
│   ├── bootstrap.min.css
│   ├── font-awesome.min.css
│   ├── landing.css
│   ├── pages.css
│   └── syntax.min.css
├── fonts
│   ├── font.js
│   ├── fontawesome.otf
│   ├── fontawesome-webfont.eot
│   ├── fontawesome-webfont.svg
│   ├── fontawesome-webfont.ttf
│   └── fontawesome-webfont.woff
├── images
│   ├── bg.png
│   ├── favicon.png
│   ├── logo.png
│   └── spinner.gif
├── javascript
│   ├── lib
│   │   ├── jquery-1.10.2.js
│   │   ├── modernizr.js
│   │   ├── payload.js
│   │   └── sidemenu.js
│   ├── plugins
│   │   ├── bootstrap.js
│   │   ├── bootstrap-affix.js
│   │   ├── bootstrap-application.js
│   │   ├── bootstrap-collapse.js
│   │   ├── bootstrap-holder.js
│   │   └── bootstrap-scrollspy.js
├── _config.yml
├── index.html
├── LICENSE
└── README.md

8 directories, 34 files
</pre>

## Support

Here are a few known issues and solutions that we came across during development. 

#### Incompatible character encodings

Getting a "Liquid Exception: incompatible character encodings: UTF-8 and IBM437..." error after running `jekyll serve` or `jekyll serve -w`. This means the CLI does not use UTF-8 by default (ex. Git for Windows). Run these commands first.

    $ cmd
    $ chcp 65001
    $ exit

You only need to run these commands when you first open your CLI. You don't need to run these commands again until you close it.

#### Conversion error

Getting a "Conversion error: There was an error converting *file_name*.md". This means an unexpected paragraph or break tag is in the Markdown file. Delete all paragraph and break tags.

#### Maruku will be deprecated

Getting a "Maruku to_s will be deprecated soon" error. This means a HTML tag is not closed. Close all HTML tags.

#### Liquid Exception: Cannot find /bin/sh

Getting a "Liquid Exception: Cannot find /bin/sh" on Windows. Make sure pygments is running on 0.5.0. While you're at it, uninstall newer versions. Run these commands.

    $ gem uninstall pygments.rb --version "=0.5.2"
    $ gem uninstall pygments.rb --version "=0.5.1"
    $ gem install pygments.rb --version "=0.5.0"

## Useful Resources

* [Jekyll's Wiki](https://github.com/mojombo/jekyll/wiki)
* [GitHub Pages](http://pages.github.com)
* [Markable.in](http://markable.in)
* [Recess](http://twitter.github.io/recess)
* [Spur](http://www.spurapp.com)
* [Setup Jekyll on Windows](http://yizeng.me/2013/05/10/setup-jekyll-on-windows)
* [Jquery UI Bootstrap](https://github.com/addyosmani/jquery-ui-bootstrap)
