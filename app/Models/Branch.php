<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Branch extends Model
{
    Use HasFactory;
    protected $table = 'branch';
    public function products(): HasMany
    {
        return  $this->hasMany(Products::class);
    }
    public function employees(): HasMany
    {
        return  $this->hasMany(Employees::class);
    }
    public function timecards(): HasMany
    {
        return  $this->hasMany(Timecards::class, 'branchid');
    }
}
