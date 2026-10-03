// Recoger entradas como texto. Python interpreta decimales, valida y calcula.
import { $ } from './dom.js';
import { state } from './config.js';

const value = (id) => $(id)?.value;

export function gather() {
  const { mode, method, source, parameter, finite, advancedType } = state;
  if (mode === 'sampling') {
    return {
      records: value('records'),
      n: value('n'),
      seed: value('seed'),
      method: advancedType.sampling,
      allocation: value('allocation'),
    };
  }

  const common = {
    confidence: value('confidence'),
    tail: value('tail') || 'two',
  };
  if (mode === 'sample') {
    return {
      ...common,
      parameter,
      finite,
      p: value('p'),
      sd: value('sd'),
      error: value('margin'),
      population: value('population'),
    };
  }
  if (mode === 'variance') {
    return {
      ...common,
      type: advancedType.variance,
      n1: value('n1'),
      n2: value('n2'),
      s1: value('s1'),
      s2: value('s2'),
      v0: value('v0'),
    };
  }
  if (mode === 'compare') {
    return {
      ...common,
      type: advancedType.compare,
      delta: value('delta'),
      a: value('listA'),
      b: value('listB'),
      mean1: value('mean1'),
      mean2: value('mean2'),
      n1: value('n1'),
      n2: value('n2'),
      s1: value('s1'),
      s2: value('s2'),
    };
  }
  if (mode === 'power') {
    return {
      ...common,
      sd: value('sd'),
      delta: value('delta'),
      n: value('n'),
      target: value('target'),
    };
  }
  return {
    ...common,
    method,
    source,
    raw: value('raw'),
    n: value('n'),
    mean: value('mean'),
    sd: value('sd'),
    success: value('success'),
    nullValue: value('nullValue'),
  };
}
