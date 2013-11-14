All of our public content is built from minimal static webpages made using [Bootstrap CSS](http://getboostrap.com), [Foundation](http://foundation.zurb.com) and [Jekyll](http://jekyllrb.com).

## Download

Two download options are available.

* [Download the latest release](https://github.com/softlayer/jumpgate/archive/master.zip)
* Clone the repo: `git clone https://github.com/softlayer/jumpgate.git gh-pages`

## Docs

Below is a list of other docs related to this project.

* [Getting Started](../getting-started)
* [Release Notes](../release-notes)
* [About](../about)

## Community

Keep track of development and community news.

* Follow [SoftLayerDevs on Twitter](http://twitter.com/softlayerdevs)
* Star any of our public [GitHub repos](http://github.com/softlayer)
* Get the latest new and join conversations on our [Customer Forum](http://forums.softlayer.com)

## Finding Support

* For more information on Jekyll, visit [Jekyll's Wiki](https://github.com/mojombo/jekyll/wiki)
* For more information on GitHub Pages, visit [GitHub Pages](http://pages.github.com)

## Running into Problems?

Here are a few known issues and solutions that we came across during development. 

#### Liquid Exception: Incompatible character encodings

* Problem: Getting a "Liquid Exception: incompatible character encodings: UTF-8 and IBM437 in index.html" error after running `jekyll serve`. 
* Cause: The CLI does not use UTF-8 by default (especially if you use Git for Windows). 
* Solution: Run these commands first.

    $ cmd
    $ chcp 65001
    $ exit

> Note: You only have to run these commands when you first open your CLI. You will not need to run these commands again until you close it.

#### Conversion error

* Problem: Getting a "Conversion error: There was an error converting '*file_name*.md'".
* Cause: An unexpected paragraph or break tag is in the markdown file.
* Solution: Delete all paragraph and break tags.

#### maruku to_s will be deprecated soon

* Problem: Getting a "maruku to_s will be deprecated soon" error.
* Cause: A HTML tag is not closed.
* Solution: Close all HTML tags.

## Copyright and License

Copyright (c) 2013 SoftLayer Technologies, Inc., an IBM Company. All content herein is licensed under the [MIT License](https://github.com/softlayer/jumpgate/blob/master/LICENSE).