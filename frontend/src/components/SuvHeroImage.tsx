import { useState } from "react";
import { HERO_MARUTI_SUV_ALT, HERO_MARUTI_SUV_IMAGE } from "./suvHeroConfig";

export default function SuvHeroImage() {
  const [failed, setFailed] = useState(false);

  return (
    <div className="suv-hero-stage" aria-label="Maruti Suzuki SUV hero">
      <div className="suv-orbit-ring suv-orbit-ring-1" />
      <div className="suv-orbit-ring suv-orbit-ring-2" />
      <div className="suv-zero-glow" />
      <div className="suv-hero-image-wrap">
        {failed ? (
          <div className="suv-hero-image-placeholder" role="img" aria-label={HERO_MARUTI_SUV_ALT}>
            <span className="suv-hero-placeholder-icon" aria-hidden>
              🚗
            </span>
            <p>Add your Maruti Suzuki SUV image:</p>
            <code>frontend/public/images/hero-maruti-suv.webp</code>
          </div>
        ) : (
          <img
            className="suv-hero-image"
            src={HERO_MARUTI_SUV_IMAGE}
            alt={HERO_MARUTI_SUV_ALT}
            width={1600}
            height={900}
            decoding="async"
            onError={() => setFailed(true)}
          />
        )}
      </div>
      <p className="suv-hero-hint">Maruti Suzuki SUV · demo imagery</p>
    </div>
  );
}
