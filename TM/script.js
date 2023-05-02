<script>
var questionNum = '%s';
var attempts = '%s';
if (attempts > 3) {
    document.getElementById("attemptStr").innerHTML = "This is question " + questionNum + ", you have no attempts left";
    document.getElementById("submitBtn").disabled = true;
} else {
    document.getElementById("attemptStr").innerHTML = "You are on question " + questionNum + " (attempt " + attempts + "/3) out of 10";
}
</script>
</html>
