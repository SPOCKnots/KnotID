var elem = document.getElementById('draw-shapes');
var two = new Two({ width: window.innerWidth - 40, height: window.innerHeight - 250}).appendTo(elem);

two.update();


var vertices = [];
var crossings = [];

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

Crossing = function(pos, angle1, angle2, index1, index2, clockwise, radius) {
    var radius = radius || 10;
    
    this.pos = pos;
    this.angle1 = angle1;
    this.angle2 = angle2;
    this.index1 = index1;
    this.index2 = index2;
    this.clockwise = clockwise;
    this.radius = radius;
    this.type = 'over';
    
    this.circle = two.makeCircle(pos.x, pos.y, radius);
    this.circle.fill = '#eee';
    this.circle.linewidth = 0;
    
    var drx = Math.cos(angle1) * this.radius
    var dry = Math.sin(angle1) * this.radius
    this.line = two.makePolygon(pos.x + drx, pos.y + dry, pos.x - drx, pos.y - dry, true);
    this.line.noFill();
    this.line.stroke = 'blue';
    this.line.linewidth = 3;
}

Crossing.prototype = {
    constructor: Crossing,
    flip: function(pos) {
        this.type = (this.type === 'over') ? 'under' : 'over';
        this.clockwise = (this.clockwise === true) ? false : true;
        this.alignLine();
        getGaussCode();
    },
    
    alignLine: function(pos) {
        var angle = (this.type === 'over') ? this.angle1 : this.angle2
        var drx = Math.cos(angle) * this.radius * 1.1
        var dry = Math.sin(angle) * this.radius * 1.1
        this.line.vertices[0].x = drx
        this.line.vertices[0].y = dry
        this.line.vertices[1].x = -1 * drx
        this.line.vertices[1].y = -1 * dry
    },
    setPos: function(pos) {
        this.pos = pos;
        this.circle.translation.set(pos.x, pos.y);
        this.line.translation.set(pos.x, pos.y);
        two.update()
    },
    undraw: function() {
        two.remove(this.circle);
        two.remove(this.line);
    }
}

function recheckCrossings(index1, index2) {
    var crossings1 = extractCrossingsWithIndex(index1);
    var newCrossings1 = findCrossings(index1, crossings1);
    crossings = crossings.concat(newCrossings1);
    
    // if (crossings.length > 2) {
    // }

    if (index2 >= vertices.length - 1) {
        return;
    }
    var crossings2 = extractCrossingsWithIndex(index2);
    var newCrossings2 = findCrossings(index2, crossings2);
    crossings = crossings.concat(newCrossings2);
}

function extractCrossingsWithIndex(index) {
    var extractedCrossings = [];
    for (var i = crossings.length-1; i >= 0; i--) {
        var crossing = crossings[i];
        if ((crossing.index1 > index && crossing.index1 < (index+1)) ||
            (crossing.index2 > index && crossing.index2 < (index+1))) {
            extractedCrossings.push(crossing);
            crossings.splice(i, 1);
        }
    }
    extractedCrossings.reverse();
    return extractedCrossings;
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
    this.circle.opacity=0.2;
    
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
    
    for (var i=0; i < vertices.length; i++) {
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

    for (var i=0; i < crossings.length; i++) {
        var crossing = crossings[i];
        distance = new Two.Vector().sub(relPos, crossing.pos).length()
        if (distance < crossing.radius) {
            crossing.flip();
            two.update();
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
    
    var vs = getSortedVertices();
    var index = 0;
    for (var i=0; i < vs.length; i++) {
        if (vs[i] === touchedVertex) {
            index = i;
            break;
        }
    }
    recheckCrossings(index-1, index);

    getGaussCode();
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
    
    touchedVertex = vertex;
    vertex.circle.fill = 'lime';
    elem.addEventListener('mousemove', moveTouchedVertex);

    two.update();
    
    getGaussCode();
};

function findCrossings(lineIndex, crossingCache) {
    
    var v1 = vertices[lineIndex].pos;
    var v2 = vertices[lineIndex + 1].pos;
    var dv = new Two.Vector().sub(v2, v1);
    
    var newCrossings = [];
    
    for (var i=0; i < lineIndex - 1; i++) {
        var ov1 = vertices[i].pos;
        var ov2 = vertices[i+1].pos;
        var odv = new Two.Vector().sub(ov2, ov1);
        var intersect = checkIntersection(v1, dv, ov1, odv);
        if (intersect[0]) {
            var crossingPos = dv.clone().multiplyScalar(intersect[1]).addSelf(v1);
            var angle1 = Math.atan2(dv.y, dv.x);
            var angle2 = Math.atan2(odv.y, odv.x);
            var index1 = i + intersect[2];
            var index2 = lineIndex + intersect[1];
            var clockwise = (crossProduct(dv.x, dv.y, odv.x, odv.y) > 0) ? false : true;
            var newCrossing = crossingFromCache(crossingCache);
            newCrossing.angle1 = angle1;
            newCrossing.angle2 = angle2;
            newCrossing.index1 = index1;
            newCrossing.index2 = index2;
            if (newCrossing.type == 'under') {
                clockwise = !clockwise;
            }
            newCrossing.clockwise = clockwise;
            newCrossing.setPos(crossingPos);
            newCrossing.alignLine();
            newCrossings.push(newCrossing)
        }
    }

    for (var i=(lineIndex + 2); i < (vertices.length-1); i++) {
        var ov1 = vertices[i].pos;
        var ov2 = vertices[i+1].pos;
        var odv = new Two.Vector().sub(ov2, ov1);
        var intersect = checkIntersection(ov1, odv, v1, dv);
        if (intersect[0]) {
            var crossingPos = dv.clone().multiplyScalar(intersect[2]).addSelf(v1);
            var angle2 = Math.atan2(dv.y, dv.x);
            var angle1 = Math.atan2(odv.y, odv.x);
            var index2 = i + intersect[1];
            var index1 = lineIndex + intersect[2];
            var clockwise = (crossProduct(odv.x, odv.y, dv.x, dv.y) > 0) ? false : true;
            var newCrossing = crossingFromCache(crossingCache);
            newCrossing.angle1 = angle1;
            newCrossing.angle2 = angle2;
            newCrossing.index1 = index1;
            newCrossing.index2 = index2;
            if (newCrossing.type == 'under') {
                clockwise = !clockwise;
            }
            newCrossing.clockwise = clockwise;
            newCrossing.setPos(crossingPos);
            newCrossing.alignLine();
            newCrossings.push(newCrossing);
        }
    }

    for (var i=0; i < crossingCache.length; i++) {
        crossingCache[i].undraw();
    }
    return newCrossings;
}

function crossingFromCache(cache) {
    if (cache.length > 0) {
        return cache.shift();
    }
    return new Crossing(new Two.Vector(0, 0), 0, 0, 0, 0, true, 10);
}

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
        if (intersect[0]) {
            var crossingPos = dv.clone().multiplyScalar(intersect[1]).addSelf(v1);
            var angle1 = Math.atan2(dv.y, dv.x);
            var angle2 = Math.atan2(odv.y, odv.x);
            var index1 = i + intersect[2];
            var index2 = vertices.length - 2 + intersect[1];
            var clockwise = (crossProduct(dv.x, dv.y, odv.x, odv.y) > 0) ? false : true;
            var newCrossing = new Crossing(crossingPos, angle1, angle2, index1, index2, clockwise, 10);
            crossings.push(newCrossing);
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
            return [true, t, u];
        }
    }
    return [false, -1, -1];
}

function crossProduct(px, py, qx, qy) {
    return px * qy - py * qx;
}

function getSortedVertices() {
    var vs = vertices.slice(0);
    vs.sort(function (a, b) {
        return a.index1 - b.index1;
    })
    return vs;
}

function getGaussCode() {
    var index = 1;
    var gc = [];
    for (var i=0; i < crossings.length; i++) {
        var crossing = crossings[i];
        gc.push([crossing.index1, index, (crossing.type === 'over') ? '-' : '+', (crossing.clockwise) ? 'c' : 'a'])
        gc.push([crossing.index2, index, (crossing.type === 'over') ? '+' : '-', (crossing.clockwise) ? 'c' : 'a'])
        index++;
    }
    gc.sort(function (a, b) {
        return a[0] - b[0];
    })
    var gcElements = gc.map(function (e) {
        return e[1].toString().concat(e[2].toString(), e[3])
    })
    
    var gcString = gcElements.join(',');
    // var gcString = ''.concat.apply(gcElements);
    
    if (gcString.length == 0) {
        gcString = '----';
    }
    
    var gcElem = document.getElementById('gc_output');
    gcElem.innerHTML = 'Gauss code: <strong>'.concat(gcString, '</strong>');
}

elem.addEventListener('mousedown', handleTouchDown);
elem.addEventListener('mouseup', handleTouchUp);
