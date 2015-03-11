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


two.update();


var vertices = [];

var touchedVertex = undefined;

function isUndefined(obj) {
    if (typeof obj === 'undefined') {
        return true
    }
    return false;
}

function getOffset(el) {
  el = el.getBoundingClientRect();
    return new Two.Vector(el.left + window.scrollX, el.top + window.scrollY);
}

Crossing = function(pos, radius) {
    radius = radius || 10;
    
    this.pos = pos;
    this.radius = radius;
    
    this.circle = two.makeCircle(pos.x, pos.y, radius);
    this.circle.fill = 'orange';
    this.circle.stroke = 'magenta';
    this.circle.linewidth = 1;
}

LineVertex = function(pos, radius) {
    this.pos = pos; 
    radius = radius || 10;
    this.radius = radius;
    
    this.previousVertex = undefined;
    this.nextVertex = undefined;
    
    this.circle = two.makeCircle(pos.x, pos.y, radius);
    this.circle.fill = 'red';
    this.circle.stroke = 'darkred';
    this.circle.linewidth = 3;
    
    this.line = two.makePolygon(pos.x, pos.y, pos.x, pos.y, true);
    this.line.noFill();
    this.line.stroke = 'blue';
    this.line.linewidth = 3;
    
    this.setPos(this.pos);
}

LineVertex.prototype = {
    constructor: LineVertex,
    setPos: function(pos) {
        this.pos = pos;
        // this.circle.translation.set(pos.x - 0.5*this.radius, 
        //                             pos.y - 0.5*this.radius);
        this.circle.translation.set(pos.x,
                                    pos.y)
        this.line.translation.set(pos.x, pos.y);
        
        var diff = new Two.Vector().sub(this.line.vertices[1], this.line.vertices[0]);
        this.line.vertices[0].x = 0;
        this.line.vertices[0].y = 0;
        this.line.vertices[1].x = diff.x;
        this.line.vertices[1].y = diff.y;

        this.positionLine();
        
        if (!isUndefined(this.nextVertex)) {
            this.nextVertex.positionLine();
        }

        two.update()
    },
    
    positionLine: function() {
        if (!isUndefined(this.previousVertex)) {
            var diff = new Two.Vector().sub(this.previousVertex.pos, this.pos);
            this.line.vertices[1].x = diff.x;
            this.line.vertices[1].y = diff.y;
        }
    }
}

function getRelPos(e) {
    var mousePos = new Two.Vector(e.clientX, e.clientY);
    var elemPos = getOffset(elem);
    var relPos = new Two.Vector(mousePos.x - elemPos.x - 5, mousePos.y - elemPos.y - 5);
    return relPos;
}

function handleTouchDown(e) {
    var relPos = getRelPos(e);
    if (!isUndefined(touchedVertex)) {
        touchedVertex.setPos( relPos );
        return
    }
    
    for (var i=0; i<vertices.length; i++) {
        var vertex = vertices[i]
        distance = new Two.Vector().sub(relPos, vertex.pos).length()
        if (distance < vertex.radius) {
            vertex.circle.fill = 'lime';
            two.update();
            touchedVertex = vertex;
            elem.addEventListener('mousemove', moveTouchedVertex);
            return
        }
    }

    addVertex(relPos);
}

function moveTouchedVertex(e) {
    if (isUndefined(touchedVertex)) {
        return
    }
    
    var relPos = getRelPos(e);
    
    touchedVertex.setPos(relPos);
}

function handleTouchUp(e) {
    if (isUndefined(touchedVertex)) {
        return
    }

    touchedVertex.circle.fill = 'red';
    two.update();
    touchedVertex = undefined;
    elem.removeEventListener('mousemove', moveTouchedVertex);
}

function addVertex(relPos) {
    var vertex = new LineVertex(relPos, 10);
    
    vertices.push( vertex );
    if (vertices.length > 1) {
        vertices[vertices.length - 1].previousVertex = vertices[vertices.length - 2];
        vertices[vertices.length - 2].nextVertex = vertices[vertices.length - 1];
    }

    vertices[vertices.length - 1].positionLine();
    
    checkForNewCrossings();

    two.update()
};

function checkForNewCrossings() {
    if (vertices.length < 2) {
        return
    }
    var v1 = vertices[vertices.length - 2].pos;
    var v2 = vertices[vertices.length - 1].pos;
    var dv = new Two.Vector().sub(v2, v1);
    for (var i=0; i < vertices.length - 3; i++) {
        var ov1 = vertices[i].pos;
        var ov2 = vertices[i+1].pos;
        var odv = new Two.Vector().sub(ov2, ov1);
        var intersect = checkIntersection(v1, dv, ov1, odv);
        console.log('intersect is', intersect);
        if (intersect[0]) {
            var crossingPos = dv.clone().multiplyScalar(intersect[1]).addSelf(v1);
            var newCrossing = Crossing(crossingPos, 10);
        }
    }
}

function checkIntersection(p, dp, q, dq) {
    var crossDiffs = crossProduct(dp.x, dp.y, dq.x, dq.y);
    if (Math.abs(crossDiffs) < 0.000001) {
        return [false, 0., 0.];
    }

    var t = crossProduct(q.x - p.x, q.y - p.y, dq.x, dq.y) / crossDiffs;
    
    if (t < 1.0 && t > 0.0) {
        u = crossProduct(q.x - p.x, q.y - p.y, dp.x, dp.y) / crossDiffs;
        if (u < 1.0 && u > 0.0) {
            console.log('found intersection between', p.x, p.y, dp.x, dp.y, q.x, q.y, dq.x, dq.y)
            return [true, t, u];
        }
    }
    return [false, -1, -1];
}

function crossProduct(px, py, qx, qy) {
    return px * qy - py * qx;
}

elem.addEventListener('mousedown', handleTouchDown);
elem.addEventListener('mouseup', handleTouchUp);
