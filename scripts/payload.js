/*! 
 * Index
 * 
 * Commitment (Chef-OpenStack) ** For demo only **
 * Milestones (Chef-OpenStack) ** For demo only **
 * Pull Requests (Chef-OpenStack) ** For demo only **
 * Commitment (Jumpgate) ** Hidden until repo goes public **
 * Milestones (Jumpgate) ** Hidden until repo goes public **
 * Pull Requests (Jumpgate) ** Hidden until repo goes public **
 * 
 */

// Commitment (Chef-OpenStack)
// Last commit date

var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/chef-openstack/commits?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;

        var stamp = new Date(latest.commit.committer.date),
            stampString = month[stamp.getMonth()] + ' ' + stamp.getDate();
        $('#commit-date').text(stampString);
    }
});

// Milestones (Chef-OpenStack)
// Next milestone date and its title

var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/chef-openstack/milestones?callback?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;

        var stamp = new Date(latest.due_on),
            stampString = month[stamp.getMonth()] + ' ' + stamp.getDate();
        $('#milestone-date').text(stampString);
        $('#milestone-title').text(latest.title);
    }
});

// (d) Pull Requests (Chef-OpenStack)
// Completed pull requests

$.ajax({
    url: "https://api.github.com/repos/softlayer/chef-openstack/pulls?state=closed?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;
        $('#closed-pulls').text(latest.number);
    }
});

// Commitment (Jumpgate)
// Last commit date and who did it

/* Hidden until repo goes public

var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/jumpgate/commits?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;

        var stamp = new Date(latest.commit.committer.date),
            stampString = month[stamp.getMonth()] + ' ' + stamp.getDate();
        $('#commit-date').text(stampString);
    }
});     */

// Milestones (Jumpgate)
// Next milestone date and its title

/* Hidden until repo goes public

var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
$.ajax({
    url: "https://api.github.com/repos/softlayer/jumpgate/milestones?callback?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;

        var stamp = new Date(latest.due_on),
            stampString = month[stamp.getMonth()] + ' ' + stamp.getDate();
        $('#milestone-date').text(stampString);
        $('#milestone-title').text(latest.title);
    }
});     */

// Pull Requests (Jumpgate)
// Completed pull requests

/* Hidden until repo goes public

$.ajax({
    url: "https://api.github.com/repos/softlayer/jumpgate/pulls?state=closed?",
    dataType: 'jsonp',
    success: function (json) {
        var latest = json.data[0];
        if (!latest) return;
        $('#closed-pulls').text(latest.number);
    }
});     */