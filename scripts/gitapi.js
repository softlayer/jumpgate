// The # of active members/stargazers

$.getJSON("https://api.github.com/orgs/softlayer/members?callback=?",

function (result) {
    var members = result.data;
    $(function () {
        $("#num-members").text(members.length);
    });
});