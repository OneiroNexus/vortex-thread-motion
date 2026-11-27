"""Build figures from the released verification JSON and explicit field formula."""
from pathlib import Path
import argparse
import json
import math
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from vortex_thread.model import segment_width

PURPLE, GOLD, TEAL = '#7161B5', '#B58A26', '#217B77'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.titleweight': 'bold', 'svg.fonttype': 'none'})

def save(fig, folder, name):
    fig.savefig(folder / (name + '.png'), dpi=220, bbox_inches='tight', facecolor='white')
    fig.savefig(folder / (name + '.svg'), bbox_inches='tight', facecolor='white')
    plt.close(fig)

def build(verification, compression, output):
    output.mkdir(parents=True, exist_ok=True)
    v = json.loads(verification.read_text(encoding='utf-8'))
    c = json.loads(compression.read_text(encoding='utf-8'))
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6), constrained_layout=True)
    x = np.linspace(0, 2*np.pi, 19, endpoint=False)
    X, Y = np.meshgrid(x, x)
    U, V = np.cos(X)*np.sin(Y), -np.sin(X)*np.cos(Y)
    ax[0].quiver(X, Y, U, V, color=PURPLE, angles='xy', scale_units='xy', scale=3.8, width=.004)
    ax[0].set(xlim=(0, 2*np.pi), ylim=(0, 2*np.pi), aspect='equal', xlabel='x (dimensionless)', ylabel='y (dimensionless)', title='Known velocity field at t = 0')
    ax[0].set_xticks([0, np.pi, 2*np.pi], ['0', r'$\pi$', r'$2\pi$'])
    ax[0].set_yticks([0, np.pi, 2*np.pi], ['0', r'$\pi$', r'$2\pi$'])
    t = np.linspace(0, 2*math.log(2), 121)
    for expanding, color, label in [(False, PURPLE, 'Contracting: y = +pi/2'), (True, TEAL, 'Expanding: y = -pi/2')]:
        width = [segment_width(.1, float(ti), .25, expanding) for ti in t]
        ax[1].plot(t, width, color=color, linewidth=2, label=label)
        ax[1].annotate(f'{width[-1]:.6f}', (t[-1], width[-1]), xytext=(-5, 7), textcoords='offset points', ha='right', color=color)
    ax[1].set(xlabel='t (dimensionless)', ylabel='Exact full segment width', title='Equal initial widths, different strain', ylim=(0, .62))
    ax[1].legend(loc='upper left', frameon=False, fontsize=9)
    ax[1].grid(alpha=.2)
    save(fig, output, 'field-and-segments')

    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4), constrained_layout=True)
    fd = v['finite_difference_convergence']
    hs = [row['h'] for row in fd]
    errors = [row['max_absolute_errors']['momentum_residual'] for row in fd]
    ax[0].loglog(hs, errors, 'o-', color=PURPLE, label='Measured residual')
    ax[0].loglog(hs, [errors[-1]*(h/hs[-1])**2 for h in hs], '--', color=GOLD, label='Second-order guide')
    ax[0].set(xlabel='Centered-difference spacing h = dt', ylabel='Max momentum residual', title='Pointwise derivative verification')
    ax[0].set_xticks(hs, [str(h) for h in hs])
    ax[0].xaxis.set_minor_formatter(NullFormatter())
    ax[0].legend(frameon=False, fontsize=9)
    tr = v['trajectory_convergence']['rows']
    steps = [row['steps'] for row in tr]
    for key, label, color in [('contracting', 'Contracting exact segment', PURPLE), ('expanding', 'Expanding exact segment', TEAL)]:
        ax[1].loglog(steps, [row['segments'][key]['absolute_error'] for row in tr], 'o-', color=color, label=label)
    ax[1].loglog(steps, [row['generic_error_against_refined_rk4'] for row in tr], 's--', color=GOLD, label='Generic vs refined RK4')
    ax[1].set(xlabel='RK4 time steps', ylabel='Absolute error', title='Passive-trajectory convergence')
    ax[1].set_xticks(steps, [str(n) for n in steps])
    ax[1].xaxis.set_minor_formatter(NullFormatter())
    ax[1].legend(frameon=False, fontsize=8)
    for a in ax:
        a.grid(which='both', alpha=.18)
    save(fig, output, 'numerical-convergence')

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), constrained_layout=True)
    labels = ['gzip 6', 'bz2 9', 'XZ/LZMA 6']
    for ax, target, title in zip(axes, ['all_columns', 'velocity_only'], ['All five numeric columns', 'Velocity columns only (unfiltered)']):
        rows = [row for row in c['results'] if row['target'] == target]
        positions = np.arange(3)
        for i, (method, label, color) in enumerate([('none', 'No transform', PURPLE), ('previous_file_xor', 'Previous-file XOR', GOLD), ('previous_point_xor', 'Previous-point XOR', TEAL)]):
            vals = [next(row['packet_bytes'] for row in rows if row['codec'] == codec and row['transform'] == method)/1000 for codec in ['gzip', 'bz2', 'lzma']]
            ax.bar(positions + (i-1)*.24, vals, width=.22, color=color, label=label)
        ax.set_xticks(positions, labels)
        ax.set(ylabel='Complete packet size (decimal kB)', title=title, ylim=(0, 440))
        ax.grid(axis='y', alpha=.2)
        ax.set_axisbelow(True)
    axes[0].legend(loc='upper left', frameon=False, fontsize=8)
    save(fig, output, 'snapshot-packet-sizes')
    print(json.dumps({'status': 'PASS', 'figures': 3, 'matplotlib': matplotlib.__version__, 'numpy': np.__version__}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verification', type=Path, default=ROOT/'results/verification-v1.0.0/verification.json')
    parser.add_argument('--compression', type=Path, default=ROOT/'results/compression-2026-11-26/compression.json')
    parser.add_argument('--output', type=Path, default=ROOT/'figures')
    args = parser.parse_args()
    build(args.verification, args.compression, args.output)
