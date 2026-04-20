const CATS = [
  { value:'maintenance', label:'Mantenimiento' },
  { value:'safety',      label:'Seguridad' },
  { value:'cleaning',    label:'Limpieza' },
  { value:'it',          label:'TI' },
  { value:'other',       label:'Otro' },
];

export default function CategoryFilter({ categories = CATS.map(c=>c.value), value, onChange }){
  const options = CATS.filter(c => categories.includes(c.value));
  return (
    <select className="input" value={value} onChange={e=>onChange(e.target.value)}>
      <option value="all">Todas las categorías</option>
      {options.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
    </select>
  );
}
