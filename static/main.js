 
var scene = new THREE.Scene();

var camera = new THREE.PerspectiveCamera( 75, 1. , 0.1, 1000 );

container = document.createElement( 'div' );
document.body.appendChild( container );

var winSize = 0.8 * window.innerHeight;
console.log('winsize', winSize);


//var renderer = new THREE.WebGLRenderer();
var renderer = new THREE.WebGLRenderer( { antialias: true } );
renderer.setSize( winSize, winSize );
renderer.setClearColor( 0xeeeeee );
container.appendChild( renderer.domElement );

stats = new Stats();
stats.domElement.style.position = 'absolute'
stats.domElement.style.top = '0px';
stats.domElement.style.right = '0px';
container.appendChild( stats.domElement )


group = new THREE.Group();
scene.add( group );


var material = new THREE.MeshPhongMaterial( { color: 0xdddddd, specular: 0.5, ambient: 0xffffff, shading: THREE.SmoothShading } )

// var material = new THREE.MeshNormalMaterial( { color: 0xdddddd, specular: 0.5, ambient: 0xffffff, shading: THREE.SmoothShading } )


scene.add( new THREE.AmbientLight( 0x333333 ) );

var pointLight = new THREE.PointLight( 0xff0000, 1);
pointLight.position.x = 40;
pointLight.position.y = 40;
pointLight.position.z = 0;
scene.add(pointLight);

var pointLight2 = new THREE.PointLight( 0x00ff00, 1);
pointLight2.position.x = -40; 
pointLight2.position.y = 40;
pointLight2.position.z = 0;
scene.add(pointLight2);

var pointLight2 = new THREE.PointLight( 0x0000ff, 1);
pointLight2.position.x = 0; 
pointLight2.position.y = -40;
pointLight2.position.z = -0;
scene.add(pointLight2);

// camera.position.z = 65;
camera.near = 0;
camera.far = 4;

controls = new THREE.OrbitControls( camera, renderer.domElement );
console.log( 'domelement', renderer.domElement );
// controls.addEventListener( 'change', render);



LinearInterpolationCurve = THREE.Curve.create(
    function ( points ) {
        this.points = points;
    },
    function ( t ) {
        var index = Math.floor( t * this.points.length );
        // console.log( 't is', t, 'length is', this.points.length, 'index is', index );
        var v1 = this.points[index % this.points.length].clone();
        var v2 = this.points[(index + 1) % this.points.length].clone();
        // console.log( 'v1 and v2 are', v1, v2 );
        
        var diff = new THREE.Vector3().subVectors( v2, v1 );
        
        // return new THREE.Vector3( Math.random(), Math.random(), Math.random() );
        return v1.add( diff.multiplyScalar( (t * this.points.length) - index ) );

    }
)


var CustomSinCurve = THREE.Curve.create( 
    function ( scale ) { //custom curve constructor 
        this.scale = (scale === undefined) ? 1 : scale;
        
    }, 

    function ( t ) { //getpoint: t is between 0-1 
        var tx = t * 3 - 1.5, ty = Math.sin( 2 * Math.pi * t ), tz = 0;
        return new THREE.Vector3(tx, ty, tz).multiplyScalar(this.scale);
    } 
);

// var path = new CustomSinCurve( 1 );
// var pathGeometry = new THREE.TubeGeometry(
//     path, 200, 0.3, 8, false );
// var pathMesh = new THREE.Mesh( pathGeometry, material );
// pathMesh.rotation.y = 0.5;
// pathMesh.rotation.x = 0.5;
// scene.add( pathMesh );

function replaceTorusKnotFromSelects() {
    var select1 = document.getElementById("select1");
    var select2 = document.getElementById("select2");

    
    replaceTorusKnot( Math.floor( select1.value ), 
                      Math.floor( select2.value ) );
}

function replaceTorusKnot(p, q) {
    if ( window.group !== undefined ) {
		scene.remove( group );
	}
    
    console.log('replacing torus knot');
    
    group = new THREE.Group();
    scene.add( group );

    var newGeometry = new THREE.TorusKnotGeometry( 2, 0.2, 128, 16, p, q );
    var newTorusKnot = new THREE.Mesh( newGeometry, material );
    newTorusKnot.position.z = -2;
    group.add( newTorusKnot );
} 
    


function render() { 
    requestAnimationFrame( render ); 
    stats.begin();
    renderer.render( scene, camera ); 
    stats.end();
    // cube.rotation.x += 0.01 + 0.001*Math.random();
    // cube.rotation.y += 0.01 + 0.001*Math.random();
    
    // var curKnot = window.group.children[0];
    // curKnot.rotation.z += 0.01;
} 
render();
