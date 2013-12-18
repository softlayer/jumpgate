# Introduction

All our public content is built from minimal static webpages made using [Bootstrap CSS](http://getboostrap.com) and [Jekyll](http://jekyllrb.com).

# Configuration

Configuring each setting for a particular project is fairly straightforward. Below is a short list that shows where you have to make updates to its configuration, including:

* config.yml
* learn-more.md
* index.html
* get-started.md
* developer-guide.md
* includes/header.html
* includes/affix-*.html
* javascript/lib/payload.js

> Note: This list only addresses content that needs to be updated/changed. 

### config.yml

The `_config.yml` file contains *almost* everything necessary to make a page on-the-fly. Open it using any editor and update the vars (defined below) before push it up to the `gh-pages` branch.

**Project**

* `project` the *public* name for the project
* `lead` high-level description for the product
* `public_url` url for the public GitHub pages

**GitHub**

* `license` url for the MIT license on the repo
* `repo` url for this GitHub repository
* `fork` url for forking the repo
* `star` url for stargazers
* `open_issues` url for open, active issues
* `closed_issues` url for closed/archives issues
* `milestones` url for this project's milestones
* `commits` url for this project's commits
* `contributors` url to show a list of contributors

**Google Analytics**

* `ga_tracking_id` SoftLayer's UA ID

### learn-more.md

* Coding Standards
* Pull Requests
* Feature Requests
* Test Cases

### index.html

* Title

### get-started.md

* About
* Specification
* Download (path to GitHub repo)
* Install
* Configure
* Addition Documentation

### developer-guide.md

Content varies from project to project. A good template to work from, though, would include Introduction, Deployment, Support, Compatibility, Useful Tools, and Next Steps.

### header.html

* Page title name
* Meta content
	* Keywords
	* Description
	* Author

### affix-*.html

Update the top-level heading (h1) to match the heading used in each of those files.

### payload.js

Change project-name in the URLs on lines 6, 28, 47, and 58.

# Directory

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
│   │   ├── affix.js
│   │   └── application.js
├── _config.yml
├── index.html
├── LICENSE
└── README.md

8 directories, 31 files
</pre>

# Support

Here are a few known issues and solutions that we came across during development. 

### Incompatible character encodings

Getting a "Liquid Exception: incompatible character encodings: UTF-8 and IBM437..." error after running `jekyll serve` or `jekyll serve -w`. This means the CLI does not use UTF-8 by default (ex. Git for Windows). Run these commands first.

    $ cmd
    $ chcp 65001
    $ exit

You only need to run these commands when you first open your CLI. You don't need to run these commands again until you close it.

### Conversion error

Getting a "Conversion error: There was an error converting *file_name*.md". This means an unexpected paragraph or break tag is in the Markdown file. Delete all paragraph and break tags.

### Maruku will be deprecated

Getting a "Maruku to_s will be deprecated soon" error. This means a HTML tag is not closed. Close all HTML tags.

### Liquid Exception: Cannot find /bin/sh

Getting a "Liquid Exception: Cannot find /bin/sh" on Windows. Make sure pygments is running on 0.5.0. While you're at it, uninstall newer versions. Run these commands.

    $ gem uninstall pygments.rb --version "=0.5.2"
    $ gem uninstall pygments.rb --version "=0.5.1"
    $ gem install pygments.rb --version "=0.5.0"

# Useful Resources

* [Jekyll's Wiki](https://github.com/mojombo/jekyll/wiki)
* [GitHub Pages](http://pages.github.com)
* [Markable.in](http://markable.in)
* [Recess](http://twitter.github.io/recess)
* [Spur](http://www.spurapp.com)
* [Setup Jekyll on Windows](http://yizeng.me/2013/05/10/setup-jekyll-on-windows)
* [jQuery UI Bootstrap](https://github.com/addyosmani/jquery-ui-bootstrap)
