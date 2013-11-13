All of our public content is built from minimal static webpages made using [Bootstrap CSS](http://getboostrap.com) and [Jekyll](http://jekyllrb.com).

## Download

Two download options are available.

* [Download the latest release](https://github.com/softlayer/slapi-stack/archive/master.zip)
* Clone the repo: `git clone https://github.com/softlayer/slapi-stack.git gh-pages`

## Community

Keep track of development and community news.

* Follow [SoftLayerDevs on Twitter](http://twitter.com/softlayerdevs)
* Star any of our public [GitHub repos](http://github.com/softlayer)
* Get the latest new and join conversations on our [Customer Forum](http://forums.softlayer.com)

## Finding Support

* For more information on Jekyll, visit [Jekyll's Wiki](https://github.com/mojombo/jekyll/wiki)
* For more information on GitHub Pages, visit [GitHub Pages](http://pages.github.com)

## Troubleshooting

1. Some consoles may throw a "Liquid Exception: incompatible character encodings: UTF-8 and IBM437 in index.html" error when you run `jekyll serve`. This means the console does not use UTF-8 by default. To get around this, run these commands first (especially if you use Git for Windows).

    $ cmd
    $ chcp 65001
    $ exit
    $ jekyll serve

You only have to run these commands when you open your console. Until the console is closed out, you will not need to run these commands again.

## Copyright and License

Copyright (c) 2013 SoftLayer Technologies, Inc., an IBM Company. All content herein is licensed under the [MIT License](https://github.com/softlayer/slapi-stack/blob/master/LICENSE).