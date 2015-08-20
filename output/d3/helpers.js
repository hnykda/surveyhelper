function wrap(text, length, center) {
  center = center || false
  ind = 0
  text.each(function() {
    if (length instanceof Array) {
      w = length[ind]-25
    } else {
      w = length
    }
    var text = d3.select(this),
        s = text.text().replace(/-/g, '- '),
        s = s.replace(/\//g, "/ "),
        words = s.split(/[\s]+/).reverse(),
        word,
        line = [],
        lineNumber = 0,
        lineHeight = 1.0, // ems
        y = text.attr("y"),
        dy = parseFloat(text.attr("dy")),
        tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em");
        if (center) {
          tspan.attr("text-anchor", "middle")
        }
    while (word = words.pop()) {
      line.push(word);
      tspan.text(line.join(" "));
      if (tspan.node().getComputedTextLength() > w) {
        line.pop();
        tspan.text(line.join(" "));
        line = [word];
        tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word)
        if (center) {
          tspan.attr("text-anchor", "middle")
        }
      }
    }
    text.attr("numlines", lineNumber+1).attr("class", "wrapped_text")
    ind += 1
  });
}
