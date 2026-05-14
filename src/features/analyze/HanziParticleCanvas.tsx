'use client';

import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { createHanziParticles } from '@/lib/three/createHanziParticles';
import { createNebulaParticles } from '@/lib/three/createNebulaParticles';

interface HanziParticleCanvasProps {
  character: string;
  progress: number; // 0 to 1
  isIdle: boolean;
}

export function HanziParticleCanvas({ character, progress, isIdle }: HanziParticleCanvasProps) {
  const mountRef = useRef<HTMLDivElement>(null);
  
  // Refs for animation
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const pointsRef = useRef<THREE.Points | null>(null);
  const geometryRef = useRef<THREE.BufferGeometry | null>(null);
  
  // Data refs
  const targetPositionsRef = useRef<Float32Array | null>(null);
  const startPositionsRef = useRef<Float32Array | null>(null);
  const currentPositionsRef = useRef<Float32Array | null>(null);
  
  // Interaction refs
  const mouseRef = useRef(new THREE.Vector2(-9999, -9999));
  const raycasterRef = useRef(new THREE.Raycaster());
  
  const targetCharacterRef = useRef(character);

  useEffect(() => {
    if (!mountRef.current) return;
    
    let isDisposed = false;
    let retryTimer: ReturnType<typeof setTimeout> | null = null;

    const mount = mountRef.current;
    const width = window.innerWidth;
    const height = window.innerHeight;
    
    // Device detection
    const isMobile = width < 768;
    const maxParticles = isMobile ? 6000 : 15000;
    
    // Setup Three.js
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    
    const camera = new THREE.PerspectiveCamera(45, width / height, 1, 3000);
    camera.position.z = Math.max(width, height) * 0.7; 
    cameraRef.current = camera;
    
    let renderer: THREE.WebGLRenderer;
    let geometry: THREE.BufferGeometry;
    let material: THREE.PointsMaterial;
    
    try {
      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: false });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
      renderer.setSize(width, height);
      mount.appendChild(renderer.domElement);
      rendererRef.current = renderer;

      /**
       * Build (or rebuild) particle geometry from the sampled character pixels.
       * Separated into a function so we can retry if the first sample returns
       * zero particles — this happens during SPA navigations when the browser's
       * font rasterizer hasn't finished loading CJK glyphs yet.
       */
      const buildParticles = () => {
        const targetPositions = createHanziParticles(character, width, height, maxParticles);
        const numParticles = targetPositions.length / 3;

        if (numParticles === 0 && !isDisposed) {
          // Font likely hasn't rasterized CJK glyphs yet; retry after a short delay
          retryTimer = setTimeout(() => {
            if (!isDisposed) buildParticles();
          }, 300);
          return;
        }

        const startPositions = createNebulaParticles(numParticles, width, height);
      
        const currentPositions = new Float32Array(targetPositions.length);
        for (let i = 0; i < currentPositions.length; i++) {
          currentPositions[i] = startPositions[i];
        }
      
        targetPositionsRef.current = targetPositions;
        startPositionsRef.current = startPositions;
        currentPositionsRef.current = currentPositions;
        targetCharacterRef.current = character;

        // Dispose old geometry if this is a retry
        if (geometryRef.current) {
          scene.remove(pointsRef.current!);
          geometryRef.current.dispose();
        }

        geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(currentPositions, 3));
      
        const colors = new Float32Array(numParticles * 3);
        const color1 = new THREE.Color('#fdfbf7');
        const color2 = new THREE.Color('#e5d5b5');
        const tempColor = new THREE.Color();
      
        for(let i=0; i<numParticles; i++) {
          tempColor.lerpColors(color1, color2, Math.random());
          colors[i*3] = tempColor.r;
          colors[i*3+1] = tempColor.g;
          colors[i*3+2] = tempColor.b;
        }
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometryRef.current = geometry;

        if (!material) {
          material = new THREE.PointsMaterial({
            size: isMobile ? 3.0 : 4.5,
            vertexColors: true,
            blending: THREE.AdditiveBlending,
            transparent: true,
            opacity: 0.9,
            depthWrite: false,
          });
        }
      
        const points = new THREE.Points(geometry, material);
        scene.add(points);
        pointsRef.current = points;
      };

      buildParticles();

      const handlePointerMove = (e: PointerEvent) => {
        mouseRef.current.x = (e.clientX / window.innerWidth) * 2 - 1;
        mouseRef.current.y = -(e.clientY / window.innerHeight) * 2 + 1;
      };
      window.addEventListener('pointermove', handlePointerMove);
      
      const handleResize = () => {
        if (isDisposed || !mountRef.current || !cameraRef.current || !rendererRef.current) return;
        const w = mountRef.current.clientWidth;
        const h = mountRef.current.clientHeight;
        cameraRef.current.aspect = w / h;
        cameraRef.current.updateProjectionMatrix();
        rendererRef.current.setSize(w, h);
      };
      window.addEventListener('resize', handleResize);

      return () => {
        isDisposed = true;
        if (retryTimer) clearTimeout(retryTimer);
        window.removeEventListener('pointermove', handlePointerMove);
        window.removeEventListener('resize', handleResize);
        if (mount && renderer) {
          mount.removeChild(renderer.domElement);
        }
        geometry?.dispose();
        material?.dispose();
        renderer?.dispose();
      };
    } catch (e) {
      console.error("Three.js initialization failed", e);
    }
  }, []);



  // Animation Loop
  useEffect(() => {
    let animationFrameId: number;
    let time = 0;
    
    const planeZ = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
    const mouseWorldPos = new THREE.Vector3();

    const animate = () => {
      time += 0.01;
      
      const geometry = geometryRef.current;
      const startPos = startPositionsRef.current;
      const targetPos = targetPositionsRef.current;
      const currentPos = currentPositionsRef.current;
      const points = pointsRef.current;
      const camera = cameraRef.current;
      
      if (geometry && startPos && targetPos && currentPos && points && camera) {
        raycasterRef.current.setFromCamera(mouseRef.current, camera);
        raycasterRef.current.ray.intersectPlane(planeZ, mouseWorldPos);
        
        const positions = geometry.attributes.position.array as Float32Array;
        const count = positions.length / 3;
        
        const repelRadius = 80;
        const repelForce = 150;
        
        for (let i = 0; i < count; i++) {
          const ix = i * 3;
          const iy = i * 3 + 1;
          const iz = i * 3 + 2;
          
          const p = progress;
          const easedP = 1 - Math.pow(1 - p, 3); // easeOutCubic
          
          let bx = startPos[ix] + (targetPos[ix] - startPos[ix]) * easedP;
          let by = startPos[iy] + (targetPos[iy] - startPos[iy]) * easedP;
          let bz = startPos[iz] + (targetPos[iz] - startPos[iz]) * easedP;
          
          if (isIdle) {
             bx += Math.sin(time * 2 + i) * 1.5;
             by += Math.cos(time * 2.5 + i) * 1.5;
          }
          
          let cx = currentPos[ix];
          let cy = currentPos[iy];
          let cz = currentPos[iz];
          
          if (progress > 0.5) {
             const dx = cx - mouseWorldPos.x;
             const dy = cy - mouseWorldPos.y;
             const distSq = dx * dx + dy * dy;
             
             if (distSq < repelRadius * repelRadius) {
                const dist = Math.sqrt(distSq);
                const force = (repelRadius - dist) / repelRadius;
                
                bx += (dx / dist) * force * repelForce;
                by += (dy / dist) * force * repelForce;
                bz += force * repelForce * 0.5;
             }
          }
          
          cx += (bx - cx) * 0.1;
          cy += (by - cy) * 0.1;
          cz += (bz - cz) * 0.1;
          
          currentPos[ix] = cx;
          currentPos[iy] = cy;
          currentPos[iz] = cz;
          
          positions[ix] = cx;
          positions[iy] = cy;
          positions[iz] = cz;
        }
        
        geometry.attributes.position.needsUpdate = true;
        
        if (isIdle) {
           points.rotation.y = Math.sin(time * 0.5) * 0.05;
           points.rotation.x = Math.cos(time * 0.3) * 0.02;
        } else {
           points.rotation.y *= 0.95;
           points.rotation.x *= 0.95;
        }
      }
      
      if (rendererRef.current && sceneRef.current && cameraRef.current) {
        rendererRef.current.render(sceneRef.current, cameraRef.current);
      }
      animationFrameId = requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [progress, isIdle]);

  return <div ref={mountRef} className="absolute inset-0 z-[3] h-full w-full pointer-events-auto" />;
}
