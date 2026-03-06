import React from 'react';
import type { JTBDCategoryData } from '../hooks/useJTBD';
import './JTBDCategory.css';

interface JTBDCategoryProps {
  category: JTBDCategoryData;
}

const JTBDCategory: React.FC<JTBDCategoryProps> = ({ category }) => {
  return (
    <div className="jtbd-category" style={{ '--category-color': category.color } as React.CSSProperties}>
      <div className="jtbd-category-header">
        <span className="jtbd-category-icon">{category.icon}</span>
        <h3 className="jtbd-category-title">{category.title}</h3>
        <span className="jtbd-category-count">{category.items.length}</span>
      </div>
      
      <div className="jtbd-category-items">
        {category.items.map((item, idx) => (
          <div key={idx} className="jtbd-category-item">
            <div className="jtbd-item-header">
              <strong className="jtbd-item-primary">{item.primary}</strong>
              {item.secondary && (
                <span className="jtbd-item-badge">{item.secondary}</span>
              )}
            </div>
            
            {item.context && (
              <p className="jtbd-item-context">
                <strong>Контекст:</strong> {item.context}
              </p>
            )}
            
            {item.quote && (
              <blockquote className="jtbd-item-quote">
                "{item.quote}"
              </blockquote>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default JTBDCategory;
