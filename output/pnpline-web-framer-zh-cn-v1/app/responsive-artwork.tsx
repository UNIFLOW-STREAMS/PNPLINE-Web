import {useEffect, useRef, useState} from 'react';

const assetRoot = '/assets/industrial-3d-web-v1';
const warehouseSizes = '(max-width: 900px) 90vw, (max-width: 1800px) 94vw, 1672px';
const warehouseWidths = [640, 960, 1440, 1920, 2172];
const cardWidths = [480, 800, 1200];

function imageSource(name: string, width: number) {
  return `${assetRoot}/${name}-${width}.webp`;
}

function responsiveSources(name: string, widths: number[]) {
  return widths.map(width => `${imageSource(name, width)} ${width}w`).join(', ');
}

export function CardArtwork({name, alt, className, sizes}: {
  name: string;
  alt: string;
  className?: string;
  sizes: string;
}) {
  return <img
    className={className}
    src={imageSource(name, 800)}
    srcSet={responsiveSources(name, cardWidths)}
    sizes={sizes}
    width={1536}
    height={1024}
    alt={alt}
    loading="lazy"
    decoding="async"
  />;
}

export function WarehouseArtwork({alt}: {alt: string}) {
  const imageRef = useRef<HTMLImageElement>(null);
  const [decoded, setDecoded] = useState(false);

  useEffect(() => {
    const image = imageRef.current;
    if (!image) return;

    function reveal() {
      if (!image?.naturalWidth) return;
      const source = image.currentSrc;
      void image.decode().then(() => {
        if (imageRef.current === image && image.currentSrc === source) setDecoded(true);
      }).catch(() => {
        // Keep the preview if the selected image fails to decode.
      });
    }

    image.addEventListener('load', reveal);
    if (image.complete) reveal();
    return () => image.removeEventListener('load', reveal);
  }, []);

  return <>
    <img
      ref={imageRef}
      className="art warehouse-floor warehouse-panorama"
      data-decoded={decoded}
      src={imageSource('warehouse-panorama', 1440)}
      srcSet={responsiveSources('warehouse-panorama', warehouseWidths)}
      sizes={warehouseSizes}
      width={2172}
      height={724}
      alt={alt}
      loading="lazy"
      decoding="async"
    />
    <img
      className="art warehouse-floor warehouse-preview"
      src={`${assetRoot}/warehouse-panorama-preview.webp`}
      width={96}
      height={32}
      alt=""
      aria-hidden="true"
      fetchPriority="low"
    />
  </>;
}
