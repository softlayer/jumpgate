All of our public content is built from minimal static webpages made using [Bootstrap CSS](http://getboostrap.com), [Foundation](http://foundation.zurb.com) and [Jekyll](http://jekyllrb.com).

## Download

* [Download the latest release](https://github.com/softlayer/jumpgate/archive/master.zip)
* Clone the repo: `git clone -b gh-pages https://github.com/softlayer/jumpgate.git`

## Workarounds for Developers

Here are a few known issues and solutions that we came across during development. 

#### Incompatible Character Encodings

Getting a "Liquid Exception: incompatible character encodings: UTF-8 and IBM437 in index.html" error after running `jekyll serve`. This means the CLI does not use UTF-8 by default (especially if you're using Git for Windows). Run these commands first.

	$ cmd
	$ chcp 65001
	$ exit

You only have to run these commands when you first open your CLI. You will not need to run these commands again until you close it.

#### Conversion Error

Getting a "Conversion error: There was an error converting '*file_name*.md'". This means an unexpected paragraph or break tag is in the markdown file. Delete all paragraph and break tags.

#### Maruku will be Deprecated

Getting a "maruku to_s will be deprecated soon" error. This means a HTML tag is not closed. Close all HTML tags.

#### Liquid Exception: Cannot find /bin/sh on Windows

Getting a "Liquid Exception: Cannot find /bin/sh" on Windows. Make sure that pygments is running on 0.5.0. At the same time, make sure that newer versions are uninstalled.

  $ gem uninstall pygments.rb --version "=0.5.2"
  $ gem uninstall pygments.rb --version "=0.5.1"
  $ gem install pygments.rb --version "=0.5.0"


## Copyright and License

Copyright (c) 2013 SoftLayer Technologies, Inc., an IBM Company. All content herein is licensed under the [MIT License](https://github.com/softlayer/jumpgate/blob/master/LICENSE).
