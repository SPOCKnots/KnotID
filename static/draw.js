var elem = document.getElementById('draw-shapes');
var two = new Two({ width: window.innerWidth - 40, height: window.innerHeight - 200}).appendTo(elem);

var circle = two.makeCircle(100, 100, 50);
var rect = two.makeRectangle(100, 200, 100, 100);
circle.fill = '#FF8000';
rect.fill = 'rgba(0, 200, 255, 0.75)';

var line = two.makePolygon(30, 30, 100, 100, 200, 500, 300, 200, true);
line.fill = 'rgba(0, 0, 0, 0)';
line.linewidth = 6;
line.stroke = 'red';

/* var group = two.makeGroup(circle, rect);
   /* group.translation.set(two.width / 2, two.height / 2); */
/* group.noStroke(); */

console.log(rect._renderer.elem);

two.update();


var vertices = [];

function getOffset(el) {
  el = el.getBoundingClientRect();
    return new Two.Vector(el.left + window.scrollX, el.top + window.scrollY);
}


LineVertex = function(pos, radius) {
    this.pos = pos; 
    radius = radius || 10
    this.radius = radius;
    
    console.log('pos radius', pos, radius);
    this.circle = two.makeCircle(pos.x, pos.y, radius);
    this.circle.fill = 'red';
    this.circle.stroke = 'darkred';
    this.circle.linewidth = 3;
    
    if (vertices.length > 0) {
        var vertex = vertices[vertices.length - 1];
        this.line = two.makePolygon(pos.x, pos.y, vertex.pos.x, vertex.pos.y, true);
        this.line.noFill();
        this.line.stroke = 'blue';
        this.line.linewidth = 3;
    }
}


function handleTouch(e) {
    var mousePos = new Two.Vector(e.clientX, e.clientY);
    var elemPos = getOffset(elem);
    var relPos = new Two.Vector(mousePos.x - elemPos.x, mousePos.y - elemPos.y);
    
    for (var i=0; i<vertices.length; i++) {
        var vertex = vertices[i]
        distance = new Two.Vector().sub(relPos, vertex.pos).length()
        if (distance < vertex.radius) {
            vertex.circle.fill = 'lightgreen';
            two.update()
            return
        }
    }

    addVertex(relPos);
}

function addVertex(relPos) {
    var vertex = new LineVertex(relPos);
    
    vertices.push( vertex );
        

    two.update()
};

elem.addEventListener('mousedown', handleTouch);
