# Jekyll

To put it simply, Jekyll is a text transformation engine. The concept behind Jekyll is like this.

1. You write text using your preferred markup language (Markdown, Textile, HTML).
2. You serve your text up to Jekyll.
3. Jekyll churns your text through a single layout (or a series of layouts).

> These instructions were written for Windows. Adjustments may be necessary if you're using a different OS.

## Getting Started

Things to download before diving into these instructions.

* [Git for Windows](http://code.google.com/p/msysgit/downloads/detail?name=Git-1.8.4-preview20130916.exe&can=2&q=full+installer+official+git)
* Ruby 2.0.0 or greater [x86](http://dl.bintray.com/oneclick/rubyinstaller/rubyinstaller-2.0.0-p247.exe?direct) or [x64](http://dl.bintray.com/oneclick/rubyinstaller/rubyinstaller-2.0.0-p247-x64.exe?direct)
* Development Kit for Ruby [x86](http://rubyforge.org/frs/download.php/76805/DevKit-mingw64-32-4.7.2-20130224-1151-sfx.exe) or [x64](http://rubyforge.org/frs/download.php/76808/DevKit-mingw64-64-4.7.2-20130224-1432-sfx.exe)

### Install Git

The installer for Git is self-explanatory. It walks you through the entire install process. If you run into any issues, [check out Git's documentation and videos on their website](http://git-scm.com/doc).

### Install Ruby

1. Open Git and run these commands. This will create the install directories.

  $ mkdir c:\ruby
  $ mkdir c:\devkit

2. Install Ruby into the `c:\ruby` directory.
3. Install DevKit into the `c:\devkit` directory.
4. Open Git and run these commands. The last command will put you back in your $HOME directory.

  $ cd c:\devkit
  $ ruby dk.rb init
  $ ruby dk.rb install
  $ cd $HOME

5. If you get any errors, go to `c:\devkit` and open `config.yml`. Verify that your Ruby directory is listed correctly.

### Install Jekyll

Run the following commands in Git. This will install Jekyll and create your first new website directory.

  $ gem install jekyll
  $ jekyll new your-website-name
  $ cd your-website-name
  $ jekyll serve

Verify that your website is "up" by opening a browser and going to [http://localhost:4000](http://localhost:4000).

# Stylus

Intro

> Again, these instructions were written for Windows. Adjustments may be necessary if you're using a different OS.

## Getting Started

Things to download before diving into these instructions. (Note: This list may include items listed in the Jekyll instructions above.)

* [Git for Windows](http://code.google.com/p/msysgit/downloads/detail?name=Git-1.8.4-preview20130916.exe&can=2&q=full+installer+official+git)
* Ruby 2.0.0 or greater [x86](http://dl.bintray.com/oneclick/rubyinstaller/rubyinstaller-2.0.0-p247.exe?direct) or [x64](http://dl.bintray.com/oneclick/rubyinstaller/rubyinstaller-2.0.0-p247-x64.exe?direct)
* Development Kit for Ruby [x86](http://rubyforge.org/frs/download.php/76805/DevKit-mingw64-32-4.7.2-20130224-1151-sfx.exe) or [x64](http://rubyforge.org/frs/download.php/76808/DevKit-mingw64-64-4.7.2-20130224-1432-sfx.exe)