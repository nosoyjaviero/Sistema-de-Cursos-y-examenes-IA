import { useEffect, useRef, useState, useCallback, useId } from "react";
import { SmiDrawer } from "smiles-drawer";

/**
 * Editor Químico Interactivo Avanzado
 *
 * Características:
 * - Múltiples estructuras SMILES (separadas por ;)
 * - Panel de herramientas para insertar estructuras comunes
 * - Átomos, enlaces, grupos funcionales
 * - Vista previa en tiempo real
 */

// ==========================================
// 🧪 BIBLIOTECA COMPLETA PARA QUÍMICA GENERAL
// ==========================================

const ESTRUCTURAS_COMUNES = {
  // ═══════════════════════════════════════════
  // 🔥 HIDROCARBUROS - Alcanos, Alquenos, Alquinos
  // ═══════════════════════════════════════════
  alcanos: [
    { nombre: "Metano", smiles: "C", emoji: "CH₄" },
    { nombre: "Etano", smiles: "CC", emoji: "C₂H₆" },
    { nombre: "Propano", smiles: "CCC", emoji: "C₃H₈" },
    { nombre: "Butano", smiles: "CCCC", emoji: "C₄H₁₀" },
    { nombre: "Pentano", smiles: "CCCCC", emoji: "C₅H₁₂" },
    { nombre: "Hexano", smiles: "CCCCCC", emoji: "C₆H₁₄" },
    { nombre: "Heptano", smiles: "CCCCCCC", emoji: "C₇H₁₆" },
    { nombre: "Octano", smiles: "CCCCCCCC", emoji: "C₈H₁₈" },
    { nombre: "Isobutano", smiles: "CC(C)C", emoji: "🔀" },
    { nombre: "Isopentano", smiles: "CC(C)CC", emoji: "🔀" },
    { nombre: "Neopentano", smiles: "CC(C)(C)C", emoji: "🔀" },
  ],
  alquenos: [
    { nombre: "Eteno (Etileno)", smiles: "C=C", emoji: "═" },
    { nombre: "Propeno", smiles: "CC=C", emoji: "C₃H₆" },
    { nombre: "1-Buteno", smiles: "CCC=C", emoji: "C₄H₈" },
    { nombre: "2-Buteno", smiles: "CC=CC", emoji: "C₄H₈" },
    { nombre: "Isobutileno", smiles: "CC(=C)C", emoji: "🔀" },
    { nombre: "1,3-Butadieno", smiles: "C=CC=C", emoji: "══" },
    { nombre: "1-Penteno", smiles: "CCCC=C", emoji: "C₅H₁₀" },
    { nombre: "2-Metil-2-buteno", smiles: "CC=C(C)C", emoji: "🔀" },
  ],
  alquinos: [
    { nombre: "Etino (Acetileno)", smiles: "C#C", emoji: "≡" },
    { nombre: "Propino", smiles: "CC#C", emoji: "C₃H₄" },
    { nombre: "1-Butino", smiles: "CCC#C", emoji: "C₄H₆" },
    { nombre: "2-Butino", smiles: "CC#CC", emoji: "C₄H₆" },
    { nombre: "1-Pentino", smiles: "CCCC#C", emoji: "C₅H₈" },
    { nombre: "1-Hexino", smiles: "CCCCC#C", emoji: "C₆H₁₀" },
  ],

  // ═══════════════════════════════════════════
  // ⬡ ANILLOS Y CICLOS
  // ═══════════════════════════════════════════
  anillos: [
    { nombre: "Benceno", smiles: "c1ccccc1", emoji: "⬡" },
    { nombre: "Ciclohexano", smiles: "C1CCCCC1", emoji: "⬢" },
    { nombre: "Ciclopentano", smiles: "C1CCCC1", emoji: "⭐" },
    { nombre: "Ciclopropano", smiles: "C1CC1", emoji: "△" },
    { nombre: "Ciclobutano", smiles: "C1CCC1", emoji: "□" },
    { nombre: "Cicloheptano", smiles: "C1CCCCCC1", emoji: "⬡⁺" },
    { nombre: "Ciclooctano", smiles: "C1CCCCCCC1", emoji: "⬢⁺" },
    { nombre: "Ciclohexeno", smiles: "C1CCC=CC1", emoji: "⬡═" },
    { nombre: "Ciclohexadieno", smiles: "C1CC=CC=C1", emoji: "⬡══" },
    { nombre: "Naftaleno", smiles: "c1ccc2ccccc2c1", emoji: "⬡⬡" },
    { nombre: "Antraceno", smiles: "c1ccc2cc3ccccc3cc2c1", emoji: "⬡⬡⬡" },
    { nombre: "Fenantreno", smiles: "c1ccc2c(c1)ccc3ccccc32", emoji: "⬡⟨⬡" },
  ],

  // ═══════════════════════════════════════════
  // 🔵 HETEROCICLOS (Anillos con N, O, S)
  // ═══════════════════════════════════════════
  heterociclos: [
    { nombre: "Piridina", smiles: "c1ccncc1", emoji: "🔵N" },
    { nombre: "Pirimidina", smiles: "c1cncnc1", emoji: "🔵NN" },
    { nombre: "Pirazina", smiles: "c1cnccn1", emoji: "🔵para" },
    { nombre: "Furano", smiles: "c1ccoc1", emoji: "🟤O" },
    { nombre: "Tiofeno", smiles: "c1ccsc1", emoji: "🟡S" },
    { nombre: "Pirrol", smiles: "c1cc[nH]c1", emoji: "🔴NH" },
    { nombre: "Imidazol", smiles: "c1c[nH]cn1", emoji: "🔵ImH" },
    { nombre: "Pirazol", smiles: "c1cc[nH]n1", emoji: "🔵PyH" },
    { nombre: "Tiazol", smiles: "c1cscn1", emoji: "🟡NS" },
    { nombre: "Oxazol", smiles: "c1cocn1", emoji: "🟤NO" },
    { nombre: "Indol", smiles: "c1ccc2[nH]ccc2c1", emoji: "⬡🔴" },
    { nombre: "Quinolina", smiles: "c1ccc2ncccc2c1", emoji: "⬡🔵" },
    { nombre: "Purina", smiles: "c1nc2c([nH]1)ncnc2", emoji: "🧬" },
  ],

  // ═══════════════════════════════════════════
  // 🔗 GRUPOS FUNCIONALES
  // ═══════════════════════════════════════════
  grupos: [
    { nombre: "Hidroxilo -OH", smiles: "CO", emoji: "-OH" },
    { nombre: "Amino -NH₂", smiles: "CN", emoji: "-NH₂" },
    { nombre: "Carboxilo -COOH", smiles: "C(=O)O", emoji: "-COOH" },
    { nombre: "Aldehído -CHO", smiles: "CC=O", emoji: "-CHO" },
    { nombre: "Cetona C=O", smiles: "CC(=O)C", emoji: "C=O" },
    { nombre: "Éster -COO-", smiles: "CC(=O)OC", emoji: "-COO-" },
    { nombre: "Éter -O-", smiles: "COC", emoji: "-O-" },
    { nombre: "Amida -CONH₂", smiles: "CC(=O)N", emoji: "-CONH₂" },
    { nombre: "Nitro -NO₂", smiles: "C[N+](=O)[O-]", emoji: "-NO₂" },
    { nombre: "Nitrilo -CN", smiles: "CC#N", emoji: "-CN" },
    { nombre: "Sulfónico -SO₃H", smiles: "CS(=O)(=O)O", emoji: "-SO₃H" },
    { nombre: "Tiol -SH", smiles: "CS", emoji: "-SH" },
    { nombre: "Fosforilo PO₄", smiles: "OP(=O)(O)O", emoji: "PO₄" },
    { nombre: "Haluro -X", smiles: "CCl", emoji: "-Cl" },
    { nombre: "Acilo", smiles: "CC(=O)", emoji: "RCO-" },
  ],

  // ═══════════════════════════════════════════
  // 🍺 ALCOHOLES
  // ═══════════════════════════════════════════
  alcoholes: [
    { nombre: "Metanol", smiles: "CO", emoji: "CH₃OH" },
    { nombre: "Etanol", smiles: "CCO", emoji: "🍺" },
    { nombre: "1-Propanol", smiles: "CCCO", emoji: "C₃H₇OH" },
    { nombre: "2-Propanol (Isopropanol)", smiles: "CC(O)C", emoji: "🧴" },
    { nombre: "1-Butanol", smiles: "CCCCO", emoji: "C₄H₉OH" },
    { nombre: "2-Butanol", smiles: "CCC(O)C", emoji: "sec" },
    { nombre: "tert-Butanol", smiles: "CC(C)(C)O", emoji: "tert" },
    { nombre: "Etilenglicol", smiles: "OCCO", emoji: "💧💧" },
    { nombre: "Glicerol", smiles: "OCC(O)CO", emoji: "🧴✨" },
    { nombre: "Fenol", smiles: "Oc1ccccc1", emoji: "⬡OH" },
    { nombre: "Alcohol bencílico", smiles: "OCc1ccccc1", emoji: "⬡CH₂OH" },
    { nombre: "Ciclohexanol", smiles: "OC1CCCCC1", emoji: "⬢OH" },
  ],

  // ═══════════════════════════════════════════
  // 🍋 ÁCIDOS CARBOXÍLICOS
  // ═══════════════════════════════════════════
  acidos: [
    { nombre: "Ácido fórmico", smiles: "C(=O)O", emoji: "HCOOH" },
    { nombre: "Ácido acético", smiles: "CC(=O)O", emoji: "🍋" },
    { nombre: "Ácido propiónico", smiles: "CCC(=O)O", emoji: "C₃" },
    { nombre: "Ácido butírico", smiles: "CCCC(=O)O", emoji: "C₄" },
    { nombre: "Ácido valérico", smiles: "CCCCC(=O)O", emoji: "C₅" },
    { nombre: "Ácido benzoico", smiles: "c1ccc(cc1)C(=O)O", emoji: "⬡COOH" },
    { nombre: "Ácido oxálico", smiles: "C(=O)(C(=O)O)O", emoji: "(COOH)₂" },
    { nombre: "Ácido láctico", smiles: "CC(O)C(=O)O", emoji: "🥛" },
    {
      nombre: "Ácido cítrico",
      smiles: "C(C(=O)O)(CC(=O)O)(CC(=O)O)O",
      emoji: "🍊",
    },
    { nombre: "Ácido aspártico", smiles: "C(C(C(=O)O)N)C(=O)O", emoji: "Asp" },
    { nombre: "Ácido glutámico", smiles: "C(CC(=O)O)C(C(=O)O)N", emoji: "Glu" },
    { nombre: "Ácido salicílico", smiles: "c1ccc(c(c1)C(=O)O)O", emoji: "💊⬡" },
  ],

  // ═══════════════════════════════════════════
  // ⚗️ ÁCIDOS INORGÁNICOS
  // ═══════════════════════════════════════════
  acidosInorg: [
    { nombre: "Ácido clorhídrico", smiles: "Cl", emoji: "HCl" },
    { nombre: "Ácido sulfúrico", smiles: "OS(=O)(=O)O", emoji: "H₂SO₄" },
    { nombre: "Ácido nítrico", smiles: "O[N+](=O)[O-]", emoji: "HNO₃" },
    { nombre: "Ácido fosfórico", smiles: "OP(=O)(O)O", emoji: "H₃PO₄" },
    { nombre: "Ácido carbónico", smiles: "OC(=O)O", emoji: "H₂CO₃" },
    { nombre: "Ácido bórico", smiles: "OB(O)O", emoji: "H₃BO₃" },
    { nombre: "Ácido bromhídrico", smiles: "Br", emoji: "HBr" },
    { nombre: "Ácido fluorhídrico", smiles: "F", emoji: "HF" },
    { nombre: "Ácido yodhídrico", smiles: "I", emoji: "HI" },
    { nombre: "Ácido sulfhídrico", smiles: "S", emoji: "H₂S" },
    { nombre: "Ácido cianhídrico", smiles: "C#N", emoji: "HCN" },
  ],

  // ═══════════════════════════════════════════
  // 💨 BASES
  // ═══════════════════════════════════════════
  bases: [
    { nombre: "Amoniaco", smiles: "N", emoji: "NH₃" },
    { nombre: "Metilamina", smiles: "CN", emoji: "CH₃NH₂" },
    { nombre: "Dimetilamina", smiles: "CNC", emoji: "(CH₃)₂NH" },
    { nombre: "Trimetilamina", smiles: "CN(C)C", emoji: "(CH₃)₃N" },
    { nombre: "Etilamina", smiles: "CCN", emoji: "C₂H₅NH₂" },
    { nombre: "Dietilamina", smiles: "CCNCC", emoji: "(C₂H₅)₂NH" },
    { nombre: "Trietilamina", smiles: "CCN(CC)CC", emoji: "Et₃N" },
    { nombre: "Anilina", smiles: "Nc1ccccc1", emoji: "⬡NH₂" },
    { nombre: "Piridina (base)", smiles: "c1ccncc1", emoji: "🔵Py" },
    { nombre: "Hidracina", smiles: "NN", emoji: "N₂H₄" },
    { nombre: "Hidroxilamina", smiles: "NO", emoji: "NH₂OH" },
    { nombre: "Urea", smiles: "NC(=O)N", emoji: "(NH₂)₂CO" },
    { nombre: "Guanidina", smiles: "NC(=N)N", emoji: "⚡" },
  ],

  // ═══════════════════════════════════════════
  // 🧬 BIOMOLÉCULAS - Aminoácidos
  // ═══════════════════════════════════════════
  aminoacidos: [
    { nombre: "Glicina (Gly)", smiles: "NCC(=O)O", emoji: "G" },
    { nombre: "Alanina (Ala)", smiles: "CC(N)C(=O)O", emoji: "A" },
    { nombre: "Valina (Val)", smiles: "CC(C)C(N)C(=O)O", emoji: "V" },
    { nombre: "Leucina (Leu)", smiles: "CC(C)CC(N)C(=O)O", emoji: "L" },
    { nombre: "Isoleucina (Ile)", smiles: "CCC(C)C(N)C(=O)O", emoji: "I" },
    { nombre: "Serina (Ser)", smiles: "OCC(N)C(=O)O", emoji: "S" },
    { nombre: "Treonina (Thr)", smiles: "CC(O)C(N)C(=O)O", emoji: "T" },
    { nombre: "Cisteína (Cys)", smiles: "SCC(N)C(=O)O", emoji: "C" },
    { nombre: "Metionina (Met)", smiles: "CSCCC(N)C(=O)O", emoji: "M" },
    {
      nombre: "Fenilalanina (Phe)",
      smiles: "c1ccc(cc1)CC(N)C(=O)O",
      emoji: "F",
    },
    { nombre: "Tirosina (Tyr)", smiles: "c1cc(ccc1CC(C(=O)O)N)O", emoji: "Y" },
    {
      nombre: "Triptófano (Trp)",
      smiles: "c1ccc2c(c1)c(cn2)CC(C(=O)O)N",
      emoji: "W",
    },
    { nombre: "Lisina (Lys)", smiles: "C(CCN)CC(C(=O)O)N", emoji: "K" },
    { nombre: "Arginina (Arg)", smiles: "C(CC(C(=O)O)N)CN=C(N)N", emoji: "R" },
    {
      nombre: "Histidina (His)",
      smiles: "c1c([nH]cn1)CC(C(=O)O)N",
      emoji: "H",
    },
    { nombre: "Prolina (Pro)", smiles: "C1CC(NC1)C(=O)O", emoji: "P" },
  ],

  // ═══════════════════════════════════════════
  // 🍬 AZÚCARES
  // ═══════════════════════════════════════════
  azucares: [
    {
      nombre: "D-Glucosa",
      smiles: "OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@@H]1O",
      emoji: "🍬",
    },
    {
      nombre: "D-Fructosa",
      smiles: "OC[C@H]1OC(O)(CO)[C@@H](O)[C@@H]1O",
      emoji: "🍯",
    },
    {
      nombre: "D-Galactosa",
      smiles: "OC[C@H]1OC(O)[C@H](O)[C@H](O)[C@H]1O",
      emoji: "🥛",
    },
    {
      nombre: "D-Ribosa",
      smiles: "OC[C@H]1OC(O)[C@H](O)[C@@H]1O",
      emoji: "RNA",
    },
    {
      nombre: "D-Desoxirribosa",
      smiles: "OC[C@H]1OC(O)C[C@@H]1O",
      emoji: "DNA",
    },
    {
      nombre: "Sacarosa",
      smiles:
        "OC[C@H]1OC(O[C@@H]2OC(CO)[C@@H](O)[C@H](O)[C@H]2O)[C@@H](O)[C@@H](O)[C@@H]1O",
      emoji: "🧁",
    },
    {
      nombre: "Maltosa",
      smiles:
        "OC[C@H]1OC(O[C@@H]2[C@@H](O)[C@H](O)[C@@H](O)OC2CO)[C@@H](O)[C@@H](O)[C@@H]1O",
      emoji: "🍺",
    },
  ],

  // ═══════════════════════════════════════════
  // 🧬 BASES NITROGENADAS (ADN/ARN)
  // ═══════════════════════════════════════════
  basesN: [
    { nombre: "Adenina (A)", smiles: "c1nc(c2c(n1)ncn2)N", emoji: "A🧬" },
    {
      nombre: "Guanina (G)",
      smiles: "c1nc2c(n1)c(=O)[nH]c(n2)N",
      emoji: "G🧬",
    },
    { nombre: "Citosina (C)", smiles: "c1cn(c(=O)nc1N)C", emoji: "C🧬" },
    { nombre: "Timina (T)", smiles: "Cc1c[nH]c(=O)[nH]c1=O", emoji: "T🧬" },
    { nombre: "Uracilo (U)", smiles: "c1c[nH]c(=O)[nH]c1=O", emoji: "U🧬" },
    {
      nombre: "ATP",
      smiles:
        "c1nc(c2c(n1)n(cn2)[C@H]3[C@@H]([C@@H]([C@H](O3)COP(=O)([O-])OP(=O)([O-])OP(=O)([O-])[O-])O)O)N",
      emoji: "⚡",
    },
  ],

  // ═══════════════════════════════════════════
  // 💊 MOLÉCULAS IMPORTANTES
  // ═══════════════════════════════════════════
  moleculas: [
    { nombre: "Agua", smiles: "O", emoji: "💧" },
    { nombre: "Dióxido de carbono", smiles: "O=C=O", emoji: "CO₂" },
    { nombre: "Peróxido de hidrógeno", smiles: "OO", emoji: "H₂O₂" },
    { nombre: "Formaldehído", smiles: "C=O", emoji: "HCHO" },
    { nombre: "Acetaldehído", smiles: "CC=O", emoji: "CH₃CHO" },
    { nombre: "Acetona", smiles: "CC(=O)C", emoji: "🧪" },
    { nombre: "Benceno", smiles: "c1ccccc1", emoji: "⬡" },
    { nombre: "Tolueno", smiles: "Cc1ccccc1", emoji: "⬡CH₃" },
    { nombre: "Cloroformo", smiles: "C(Cl)(Cl)Cl", emoji: "CHCl₃" },
    { nombre: "Tetracloruro de C", smiles: "C(Cl)(Cl)(Cl)Cl", emoji: "CCl₄" },
    { nombre: "Cafeína", smiles: "Cn1cnc2c1c(=O)n(c(=O)n2C)C", emoji: "☕" },
    { nombre: "Aspirina", smiles: "CC(=O)Oc1ccccc1C(=O)O", emoji: "💊" },
    { nombre: "Paracetamol", smiles: "CC(=O)Nc1ccc(O)cc1", emoji: "💊" },
    { nombre: "Ibuprofeno", smiles: "CC(C)Cc1ccc(cc1)C(C)C(=O)O", emoji: "💊" },
    { nombre: "Nicotina", smiles: "CN1CCCC1c2cccnc2", emoji: "🚬" },
    {
      nombre: "Colesterol",
      smiles: "CC(C)CCCC(C)C1CCC2C1(CCC3C2CC=C4C3(CCC(C4)O)C)C",
      emoji: "🫀",
    },
  ],

  // ═══════════════════════════════════════════
  // ⚛️ ÁTOMOS
  // ═══════════════════════════════════════════
  atomos: [
    { nombre: "Carbono", smiles: "C", emoji: "C" },
    { nombre: "Hidrógeno", smiles: "[H]", emoji: "H" },
    { nombre: "Oxígeno", smiles: "O", emoji: "O" },
    { nombre: "Nitrógeno", smiles: "N", emoji: "N" },
    { nombre: "Azufre", smiles: "S", emoji: "S" },
    { nombre: "Fósforo", smiles: "P", emoji: "P" },
    { nombre: "Cloro", smiles: "Cl", emoji: "Cl" },
    { nombre: "Bromo", smiles: "Br", emoji: "Br" },
    { nombre: "Flúor", smiles: "F", emoji: "F" },
    { nombre: "Yodo", smiles: "I", emoji: "I" },
    { nombre: "Boro", smiles: "B", emoji: "B" },
    { nombre: "Silicio", smiles: "[Si]", emoji: "Si" },
    { nombre: "⊕ Carbocatión", smiles: "[CH3+]", emoji: "C⁺" },
    { nombre: "⊖ Carbanión", smiles: "[CH3-]", emoji: "C⁻" },
  ],

  // ═══════════════════════════════════════════
  // ⬡ AROMÁTICOS SUSTITUIDOS
  // ═══════════════════════════════════════════
  aromaticos: [
    { nombre: "Tolueno", smiles: "Cc1ccccc1", emoji: "⬡-Me" },
    { nombre: "Fenol", smiles: "Oc1ccccc1", emoji: "⬡-OH" },
    { nombre: "Anilina", smiles: "Nc1ccccc1", emoji: "⬡-NH₂" },
    {
      nombre: "Nitrobenceno",
      smiles: "c1ccc(cc1)[N+](=O)[O-]",
      emoji: "⬡-NO₂",
    },
    { nombre: "Clorobenceno", smiles: "Clc1ccccc1", emoji: "⬡-Cl" },
    { nombre: "Bromobenceno", smiles: "Brc1ccccc1", emoji: "⬡-Br" },
    { nombre: "Benzaldehído", smiles: "c1ccc(cc1)C=O", emoji: "⬡-CHO" },
    { nombre: "Estireno", smiles: "C=Cc1ccccc1", emoji: "⬡-CH=CH₂" },
    { nombre: "Ácido benzoico", smiles: "c1ccc(cc1)C(=O)O", emoji: "⬡-COOH" },
    { nombre: "Acetofenona", smiles: "CC(=O)c1ccccc1", emoji: "⬡-COCH₃" },
    {
      nombre: "Benzoato de metilo",
      smiles: "COC(=O)c1ccccc1",
      emoji: "⬡-COOMe",
    },
    { nombre: "Xileno (orto)", smiles: "Cc1ccccc1C", emoji: "o-xileno" },
    { nombre: "Xileno (meta)", smiles: "Cc1cccc(c1)C", emoji: "m-xileno" },
    { nombre: "Xileno (para)", smiles: "Cc1ccc(cc1)C", emoji: "p-xileno" },
    {
      nombre: "TNT",
      smiles: "Cc1c(cc(cc1[N+](=O)[O-])[N+](=O)[O-])[N+](=O)[O-]",
      emoji: "💥",
    },
  ],

  // ═══════════════════════════════════════════
  // 🔗 ÉTERES Y EPÓXIDOS
  // ═══════════════════════════════════════════
  eteres: [
    { nombre: "Dimetiléter", smiles: "COC", emoji: "CH₃OCH₃" },
    { nombre: "Dietiléter", smiles: "CCOCC", emoji: "Et₂O" },
    { nombre: "THF", smiles: "C1CCOC1", emoji: "⬢O" },
    { nombre: "Dioxano", smiles: "C1COCCO1", emoji: "⬢OO" },
    { nombre: "Anisol", smiles: "COc1ccccc1", emoji: "⬡-OMe" },
    { nombre: "Óxido de etileno", smiles: "C1CO1", emoji: "△O" },
    { nombre: "Óxido de propileno", smiles: "CC1CO1", emoji: "△O-Me" },
    { nombre: "Éter corona 18-6", smiles: "C1COCCOCCOCCOCCOCCO1", emoji: "👑" },
  ],

  // ═══════════════════════════════════════════
  // 🧪 ÉSTERES Y ANHÍDRIDOS
  // ═══════════════════════════════════════════
  esteres: [
    { nombre: "Acetato de metilo", smiles: "CC(=O)OC", emoji: "MeOAc" },
    { nombre: "Acetato de etilo", smiles: "CC(=O)OCC", emoji: "EtOAc" },
    {
      nombre: "Benzoato de metilo",
      smiles: "COC(=O)c1ccccc1",
      emoji: "⬡-COOMe",
    },
    { nombre: "Formiato de etilo", smiles: "CCOC=O", emoji: "HCOOE" },
    { nombre: "Lactona (β)", smiles: "O=C1CCO1", emoji: "β-lact" },
    { nombre: "Lactona (γ)", smiles: "O=C1CCCO1", emoji: "γ-lact" },
    { nombre: "Anhídrido acético", smiles: "CC(=O)OC(=O)C", emoji: "Ac₂O" },
    { nombre: "Anhídrido maleico", smiles: "C1=CC(=O)OC1=O", emoji: "MaleAnh" },
  ],

  // ═══════════════════════════════════════════
  // ⚡ COMPUESTOS DE AZUFRE
  // ═══════════════════════════════════════════
  azufrados: [
    { nombre: "Metanotiol", smiles: "CS", emoji: "CH₃SH" },
    { nombre: "Etanotiol", smiles: "CCS", emoji: "C₂H₅SH" },
    { nombre: "Dimetilsulfuro", smiles: "CSC", emoji: "(CH₃)₂S" },
    { nombre: "DMSO", smiles: "CS(=O)C", emoji: "(CH₃)₂SO" },
    { nombre: "Disulfuro de dimetilo", smiles: "CSSC", emoji: "MeSSMe" },
    { nombre: "Tiofeno", smiles: "c1ccsc1", emoji: "🟡S" },
    { nombre: "Cisteína", smiles: "SCC(N)C(=O)O", emoji: "Cys" },
    {
      nombre: "Sulfonamida",
      smiles: "c1ccc(cc1)S(=O)(=O)N",
      emoji: "⬡-SO₂NH₂",
    },
  ],
};

const ChemEditor = ({
  value,
  onChange,
  placeholder = "Estructura química...",
  readOnly = false,
}) => {
  const uniqueId = useId().replace(/:/g, "_");
  const drawerRef = useRef(null);
  const [inputSmiles, setInputSmiles] = useState(value || "");
  const [estructuras, setEstructuras] = useState([]);
  const [errores, setErrores] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [tabActiva, setTabActiva] = useState("alcanos");
  const [mostrarHerramientas, setMostrarHerramientas] = useState(!readOnly);

  // Inicializar drawer
  useEffect(() => {
    if (!drawerRef.current) {
      drawerRef.current = new SmiDrawer({
        width: 280,
        height: 200,
        bondThickness: 1.5,
        bondLength: 20,
        shortBondLength: 0.8,
        bondSpacing: 4,
        atomVisualization: "default",
        isomeric: true,
        debug: false,
        terminalCarbons: false,
        explicitHydrogens: false,
        compactDrawing: true,
        themes: {
          dark: {
            C: "#e9d5ff",
            O: "#ef4444",
            N: "#3b82f6",
            F: "#10b981",
            CL: "#10b981",
            BR: "#f59e0b",
            I: "#a855f7",
            P: "#f97316",
            S: "#eab308",
            B: "#ec4899",
            SI: "#94a3b8",
            H: "#cbd5e1",
            BACKGROUND: "transparent",
          },
        },
      });
    }
  }, []);

  // Sincronizar cuando value cambie desde fuera
  useEffect(() => {
    setInputSmiles(value || "");
  }, [value]);

  // Parsear múltiples estructuras separadas por ;
  useEffect(() => {
    if (!inputSmiles.trim()) {
      setEstructuras([]);
      return;
    }

    const partes = inputSmiles
      .split(";")
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

    setEstructuras(
      partes.map((smiles, idx) => ({
        id: `${uniqueId}-struct-${idx}`,
        smiles: smiles.replace(/[\r\n]+/g, "").trim(),
        drawn: false,
        error: null,
      })),
    );
  }, [inputSmiles, uniqueId]);

  // Dibujar estructuras
  const drawEstructura = useCallback((estructura, svgElement) => {
    if (!estructura.smiles || !svgElement || !drawerRef.current) return;

    svgElement.innerHTML = "";

    try {
      drawerRef.current.draw(
        estructura.smiles,
        svgElement,
        "dark",
        () => {
          setEstructuras((prev) =>
            prev.map((e) =>
              e.id === estructura.id ? { ...e, drawn: true, error: null } : e,
            ),
          );
          setErrores((prev) => ({ ...prev, [estructura.id]: null }));
        },
        (err) => {
          console.error(`Error dibujando ${estructura.smiles}:`, err);
          setEstructuras((prev) =>
            prev.map((e) =>
              e.id === estructura.id
                ? { ...e, drawn: false, error: "SMILES inválido" }
                : e,
            ),
          );
          setErrores((prev) => ({
            ...prev,
            [estructura.id]: "SMILES inválido",
          }));
        },
      );
    } catch (e) {
      console.error("Error general:", e);
      setErrores((prev) => ({ ...prev, [estructura.id]: e.message }));
    }
  }, []);

  // Efecto para dibujar todas las estructuras
  useEffect(() => {
    const timer = setTimeout(() => {
      estructuras.forEach((est) => {
        const svgEl = document.getElementById(est.id);
        if (svgEl) {
          drawEstructura(est, svgEl);
        }
      });
    }, 300);
    return () => clearTimeout(timer);
  }, [estructuras, drawEstructura]);

  const handleChange = (newValue) => {
    setInputSmiles(newValue);
    onChange?.(newValue);
  };

  // Insertar estructura desde las herramientas
  const insertarEstructura = (smiles) => {
    const nuevoValor = inputSmiles.trim()
      ? `${inputSmiles.trim()}; ${smiles}`
      : smiles;
    handleChange(nuevoValor);
  };

  // Eliminar una estructura específica
  const eliminarEstructura = (idx) => {
    const partes = inputSmiles
      .split(";")
      .map((s) => s.trim())
      .filter((s) => s.length > 0);
    partes.splice(idx, 1);
    handleChange(partes.join("; "));
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
      }}
    >
      {/* Panel de herramientas */}
      {!readOnly && (
        <div
          style={{
            background: "rgba(16, 185, 129, 0.05)",
            borderRadius: "8px",
            border: "2px solid rgba(16, 185, 129, 0.2)",
            overflow: "hidden",
          }}
        >
          {/* Header del panel */}
          <div
            onClick={() => setMostrarHerramientas(!mostrarHerramientas)}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "0.75rem 1rem",
              background: "rgba(16, 185, 129, 0.1)",
              cursor: "pointer",
              userSelect: "none",
            }}
          >
            <span style={{ color: "#6ee7b7", fontWeight: "600" }}>
              🧪 Herramientas Químicas
            </span>
            <span style={{ color: "#6ee7b7" }}>
              {mostrarHerramientas ? "▼" : "▶"}
            </span>
          </div>

          {mostrarHerramientas && (
            <div style={{ padding: "0.75rem" }}>
              {/* Tabs - Organizadas en filas por tema */}
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.5rem",
                  marginBottom: "0.75rem",
                }}
              >
                {/* Fila 1: Hidrocarburos */}
                <div
                  style={{
                    display: "flex",
                    gap: "0.25rem",
                    flexWrap: "wrap",
                    alignItems: "center",
                  }}
                >
                  <span
                    style={{
                      fontSize: "0.7rem",
                      color: "#94a3b8",
                      minWidth: "70px",
                    }}
                  >
                    🔥 Hidrocarburos:
                  </span>
                  {[
                    { key: "alcanos", label: "Alcanos" },
                    { key: "alquenos", label: "Alquenos" },
                    { key: "alquinos", label: "Alquinos" },
                    { key: "anillos", label: "⬡ Ciclos" },
                    { key: "aromaticos", label: "⬡ Aromáticos" },
                  ].map((tab) => (
                    <button
                      type="button"
                      key={tab.key}
                      onClick={() => setTabActiva(tab.key)}
                      style={{
                        padding: "0.3rem 0.5rem",
                        fontSize: "0.7rem",
                        borderRadius: "4px",
                        border: "none",
                        background:
                          tabActiva === tab.key
                            ? "rgba(16, 185, 129, 0.4)"
                            : "rgba(100, 116, 139, 0.15)",
                        color: tabActiva === tab.key ? "#6ee7b7" : "#94a3b8",
                        cursor: "pointer",
                      }}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* Fila 2: Grupos funcionales */}
                <div
                  style={{
                    display: "flex",
                    gap: "0.25rem",
                    flexWrap: "wrap",
                    alignItems: "center",
                  }}
                >
                  <span
                    style={{
                      fontSize: "0.7rem",
                      color: "#94a3b8",
                      minWidth: "70px",
                    }}
                  >
                    🔗 Funcionales:
                  </span>
                  {[
                    { key: "grupos", label: "Grupos" },
                    { key: "alcoholes", label: "🍺 Alcoholes" },
                    { key: "eteres", label: "Éteres" },
                    { key: "esteres", label: "Ésteres" },
                    { key: "heterociclos", label: "🔵 Heterociclos" },
                    { key: "azufrados", label: "S Azufrados" },
                  ].map((tab) => (
                    <button
                      type="button"
                      key={tab.key}
                      onClick={() => setTabActiva(tab.key)}
                      style={{
                        padding: "0.3rem 0.5rem",
                        fontSize: "0.7rem",
                        borderRadius: "4px",
                        border: "none",
                        background:
                          tabActiva === tab.key
                            ? "rgba(16, 185, 129, 0.4)"
                            : "rgba(100, 116, 139, 0.15)",
                        color: tabActiva === tab.key ? "#6ee7b7" : "#94a3b8",
                        cursor: "pointer",
                      }}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* Fila 3: Ácidos y Bases */}
                <div
                  style={{
                    display: "flex",
                    gap: "0.25rem",
                    flexWrap: "wrap",
                    alignItems: "center",
                  }}
                >
                  <span
                    style={{
                      fontSize: "0.7rem",
                      color: "#94a3b8",
                      minWidth: "70px",
                    }}
                  >
                    ⚗️ Ácidos/Bases:
                  </span>
                  {[
                    { key: "acidos", label: "🍋 Org." },
                    { key: "acidosInorg", label: "⚗️ Inorg." },
                    { key: "bases", label: "💨 Bases" },
                  ].map((tab) => (
                    <button
                      type="button"
                      key={tab.key}
                      onClick={() => setTabActiva(tab.key)}
                      style={{
                        padding: "0.3rem 0.5rem",
                        fontSize: "0.7rem",
                        borderRadius: "4px",
                        border: "none",
                        background:
                          tabActiva === tab.key
                            ? "rgba(16, 185, 129, 0.4)"
                            : "rgba(100, 116, 139, 0.15)",
                        color: tabActiva === tab.key ? "#6ee7b7" : "#94a3b8",
                        cursor: "pointer",
                      }}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* Fila 4: Bioquímica */}
                <div
                  style={{
                    display: "flex",
                    gap: "0.25rem",
                    flexWrap: "wrap",
                    alignItems: "center",
                  }}
                >
                  <span
                    style={{
                      fontSize: "0.7rem",
                      color: "#94a3b8",
                      minWidth: "70px",
                    }}
                  >
                    🧬 Bio:
                  </span>
                  {[
                    { key: "aminoacidos", label: "Aminoácidos" },
                    { key: "azucares", label: "🍬 Azúcares" },
                    { key: "basesN", label: "ADN/ARN" },
                  ].map((tab) => (
                    <button
                      type="button"
                      key={tab.key}
                      onClick={() => setTabActiva(tab.key)}
                      style={{
                        padding: "0.3rem 0.5rem",
                        fontSize: "0.7rem",
                        borderRadius: "4px",
                        border: "none",
                        background:
                          tabActiva === tab.key
                            ? "rgba(16, 185, 129, 0.4)"
                            : "rgba(100, 116, 139, 0.15)",
                        color: tabActiva === tab.key ? "#6ee7b7" : "#94a3b8",
                        cursor: "pointer",
                      }}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* Fila 5: General */}
                <div
                  style={{
                    display: "flex",
                    gap: "0.25rem",
                    flexWrap: "wrap",
                    alignItems: "center",
                  }}
                >
                  <span
                    style={{
                      fontSize: "0.7rem",
                      color: "#94a3b8",
                      minWidth: "70px",
                    }}
                  >
                    ⚛️ General:
                  </span>
                  {[
                    { key: "moleculas", label: "💊 Moléculas" },
                    { key: "atomos", label: "⚛️ Átomos" },
                  ].map((tab) => (
                    <button
                      type="button"
                      key={tab.key}
                      onClick={() => setTabActiva(tab.key)}
                      style={{
                        padding: "0.3rem 0.5rem",
                        fontSize: "0.7rem",
                        borderRadius: "4px",
                        border: "none",
                        background:
                          tabActiva === tab.key
                            ? "rgba(16, 185, 129, 0.4)"
                            : "rgba(100, 116, 139, 0.15)",
                        color: tabActiva === tab.key ? "#6ee7b7" : "#94a3b8",
                        cursor: "pointer",
                      }}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Contenido de la tab */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fill, minmax(90px, 1fr))",
                  gap: "0.5rem",
                  maxHeight: "200px",
                  overflowY: "auto",
                }}
              >
                {ESTRUCTURAS_COMUNES[tabActiva]?.map((item, idx) => (
                  <button
                    type="button"
                    key={idx}
                    onClick={() => insertarEstructura(item.smiles)}
                    title={`${item.nombre}: ${item.smiles}`}
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      gap: "0.25rem",
                      padding: "0.5rem",
                      background: "rgba(30, 41, 59, 0.6)",
                      border: "1px solid rgba(16, 185, 129, 0.2)",
                      borderRadius: "6px",
                      cursor: "pointer",
                      transition: "all 0.2s",
                      color: "#d1fae5",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background =
                        "rgba(16, 185, 129, 0.2)";
                      e.currentTarget.style.borderColor =
                        "rgba(16, 185, 129, 0.5)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background =
                        "rgba(30, 41, 59, 0.6)";
                      e.currentTarget.style.borderColor =
                        "rgba(16, 185, 129, 0.2)";
                    }}
                  >
                    <span style={{ fontSize: "1.2rem" }}>{item.emoji}</span>
                    <span style={{ fontSize: "0.7rem", textAlign: "center" }}>
                      {item.nombre}
                    </span>
                  </button>
                ))}
              </div>

              {/* Input manual */}
              <div style={{ marginTop: "0.75rem" }}>
                <label
                  style={{
                    display: "block",
                    color: "#94a3b8",
                    fontSize: "0.75rem",
                    marginBottom: "0.25rem",
                  }}
                >
                  💡 SMILES manual (separar múltiples con punto y coma ;)
                </label>
                <input
                  type="text"
                  value={inputSmiles}
                  onChange={(e) => handleChange(e.target.value)}
                  placeholder="Ej: c1ccccc1; CCO; CC(=O)O"
                  style={{
                    width: "100%",
                    padding: "0.5rem 0.75rem",
                    fontSize: "0.85rem",
                    fontFamily: "monospace",
                    borderRadius: "6px",
                    border: "1px solid rgba(16, 185, 129, 0.3)",
                    background: "rgba(30, 41, 59, 0.6)",
                    color: "#d1fae5",
                    outline: "none",
                  }}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Vista de estructuras - En readOnly solo muestra las moléculas visuales, no el texto SMILES */}
      {estructuras.length > 0 ? (
        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              estructuras.length === 1
                ? "1fr"
                : "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "1rem",
          }}
        >
          {estructuras.map((est, idx) => (
            <div
              key={est.id}
              style={{
                background: "rgba(30, 41, 59, 0.8)",
                borderRadius: "8px",
                border: est.error
                  ? "2px solid rgba(239, 68, 68, 0.5)"
                  : "2px solid rgba(16, 185, 129, 0.3)",
                padding: "0.75rem",
                position: "relative",
              }}
            >
              {/* Header de la estructura */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "0.5rem",
                }}
              >
                <span
                  style={{
                    color: "#6ee7b7",
                    fontSize: "0.75rem",
                    fontFamily: "monospace",
                  }}
                >
                  {est.smiles.length > 30
                    ? est.smiles.slice(0, 30) + "..."
                    : est.smiles}
                </span>
                {!readOnly && (
                  <button
                    type="button"
                    onClick={() => eliminarEstructura(idx)}
                    style={{
                      background: "rgba(239, 68, 68, 0.2)",
                      border: "none",
                      borderRadius: "4px",
                      padding: "0.25rem 0.5rem",
                      color: "#fca5a5",
                      cursor: "pointer",
                      fontSize: "0.75rem",
                    }}
                    title="Eliminar estructura"
                  >
                    ✕
                  </button>
                )}
              </div>

              {/* SVG de la estructura */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  minHeight: "200px",
                }}
              >
                {est.error ? (
                  <div
                    style={{
                      color: "#fca5a5",
                      textAlign: "center",
                      fontSize: "0.85rem",
                    }}
                  >
                    ⚠️ {est.error}
                    <br />
                    <span style={{ color: "#94a3b8", fontSize: "0.75rem" }}>
                      Verifica: {est.smiles}
                    </span>
                  </div>
                ) : (
                  <svg
                    id={est.id}
                    xmlns="http://www.w3.org/2000/svg"
                    style={{
                      width: "100%",
                      height: "200px",
                      maxWidth: "280px",
                    }}
                  />
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div
          style={{
            background: "rgba(30, 41, 59, 0.8)",
            borderRadius: "8px",
            border: "2px solid rgba(16, 185, 129, 0.3)",
            padding: "2rem",
            textAlign: "center",
            color: "#6ee7b7",
          }}
        >
          {readOnly ? (
            "No hay estructuras químicas"
          ) : (
            <>
              <span
                style={{
                  fontSize: "2rem",
                  display: "block",
                  marginBottom: "0.5rem",
                }}
              >
                🧪
              </span>
              Selecciona una estructura del panel o escribe SMILES
            </>
          )}
        </div>
      )}

      {/* Referencia rápida */}
      {!readOnly && (
        <div
          style={{
            background: "rgba(100, 116, 139, 0.1)",
            borderRadius: "6px",
            padding: "0.75rem",
            fontSize: "0.75rem",
            color: "#94a3b8",
          }}
        >
          <strong>📖 Referencia SMILES:</strong> <code>c1ccccc1</code>=Benceno,{" "}
          <code>C</code>=Carbono, <code>=</code>=Doble enlace,
          <code>#</code>=Triple, <code>()</code>=Ramificación, <code>[]</code>
          =Átomo especial
        </div>
      )}
    </div>
  );
};

export default ChemEditor;
