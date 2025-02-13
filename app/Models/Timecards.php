<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Timecards extends Model
{
    use HasFactory;
    public function branch(): HasMany
    {
        return  $this->hasMany(Branch::class);
    }

    public function employees(): HasMany
    {
        return  $this->hasMany(Employees::class);
    }
}
